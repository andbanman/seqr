from collections import defaultdict
import hail as hl
import logging

from seqr.views.utils.json_utils import _to_camel_case
from reference_data.models import GENOME_VERSION_GRCh37
from seqr.models import Sample, Individual
from seqr.utils.elasticsearch.utils import InvalidSearchException
from seqr.utils.elasticsearch.constants import RECESSIVE, COMPOUND_HET, X_LINKED_RECESSIVE, ANY_AFFECTED, \
    INHERITANCE_FILTERS, ALT_ALT, REF_REF, REF_ALT, HAS_ALT, HAS_REF, MAX_NO_LOCATION_COMP_HET_FAMILIES, SPLICE_AI_FIELD, \
    CLINVAR_SIGNFICANCE_MAP, HGMD_CLASS_MAP, CLINVAR_PATH_FILTER, CLINVAR_LIKELY_PATH_FILTER, PATH_FREQ_OVERRIDE_CUTOFF
from seqr.utils.elasticsearch.es_search import EsSearch, _get_family_affected_status

logger = logging.getLogger(__name__)

#  For production: constants should have their own file

GENOTYPE_QUERY_MAP = {
    REF_REF: lambda gt: gt.is_hom_ref(),
    REF_ALT: lambda gt: gt.is_het(),
    ALT_ALT: lambda gt: gt.is_hom_var(),
    HAS_ALT: lambda gt: gt.is_non_ref(),
    HAS_REF: lambda gt: gt.is_hom_ref() | gt.is_het_ref(),
}

POPULATION_SUB_FIELDS = {
    'AF',
    'AC',
    'AN',
    'Hom',
    'Hemi',
    'Het',
}
POPULATIONS = {
    'topmed': {'hemi': None,'het': None},
    'g1k': {'filter_af': 'POPMAX_AF', 'hom': None, 'hemi': None, 'het': None},
    'exac': {
        'filter_af': 'AF_POPMAX', 'ac': 'AC_Adj', 'an': 'AN_Adj', 'hom': 'AC_Hom', 'hemi': 'AC_Hemi', 'het': None,
    },
    'gnomad_exomes': {'filter_AF':  'AF_POPMAX_OR_GLOBAL', 'het': None},
    'gnomad_genomes': {'filter_af': 'AF_POPMAX_OR_GLOBAL', 'het': None},
}
for pop_config in POPULATIONS.values():
    pop_config.update({field.lower(): field for field in POPULATION_SUB_FIELDS if field.lower() not in pop_config})

PREDICTION_FIELDS_CONFIG = {}
for path, pred_config in {
    'cadd': {'PHRED': 'cadd'},
    'dbnsfp': {
        'FATHMM_pred': 'fathmm',
        'GERP_RS': 'gerp_rs',
        'MetaSVM_pred': 'metasvm',
        'MutationTaster_pred': 'mutationtaster',
        'phastCons100way_vertebrate': 'phastcons_100_vert',
        'Polyphen2_HVAR_pred': 'polyphen',
        'REVEL_score': 'revel',
        'SIFT_pred': 'sift',
    },
    'eigen': {'Eigen_phred': 'eigen'},
    'mpc': {'MPC': 'mpc'},
    'primate_ai': {'score': 'primate_ai'},
    'splice_ai': {'delta_score': 'splice_ai', 'splice_consequence': 'splice_ai_consequence'},
}.items():
    PREDICTION_FIELDS_CONFIG.update({prediction: (path, sub_path) for sub_path, prediction in pred_config.items()})

GENOTYPE_FIELDS = ['familyGuids', 'genotypes']
CORE_FIELDS = ['hgmd', 'rsid', 'xpos']
ANNOTATION_FIELDS = {
    'chrom': lambda r: r.locus.contig.replace("^chr", ""),
    'pos': lambda r: r.locus.position,
    'ref': lambda r: r.alleles[0],
    'alt': lambda r: r.alleles[1],
    'clinvar': lambda r: hl.struct(
        clinicalSignificance=r.clinvar.clinical_significance,
        alleleId=r.clinvar.allele_id,
        goldStars=r.clinvar.gold_stars,
    ),
    'genotypeFilters': lambda r: hl.str(' ,').join(r.filters),
    'genomeVersion': lambda r: hl.eval(r.gv),
    'liftedOverGenomeVersion': lambda r: hl.if_else(
        hl.is_defined(r.rg37_locus), hl.literal(GENOME_VERSION_GRCh37), hl.missing(hl.dtype('str')),
    ),
    'liftedOverChrom': lambda r: hl.if_else(
        hl.is_defined(r.rg37_locus), r.rg37_locus.contig, hl.missing(hl.dtype('str')),
    ),
    'liftedOverPos': lambda r: hl.if_else(
        hl.is_defined(r.rg37_locus), r.rg37_locus.position, hl.missing(hl.dtype('int32')),
    ),
    'mainTranscriptId': lambda r: r.sortedTranscriptConsequences[0].transcript_id,
    'originalAltAlleles': lambda r: r.originalAltAlleles.map(lambda a: a.split('-')[-1]),
    'populations': lambda r: hl.struct(callset=hl.struct(af=r.AF, ac=r.AC, an=r.AN), **{
        population: hl.struct(**{
            response_key: hl.or_else(r[population][field], 0) for response_key, field in pop_config.items()
            if field is not None
        }) for population, pop_config in POPULATIONS.items()}
    ),
    'predictions': lambda r: hl.struct(**{
        prediction: r[path[0]][path[1]] for prediction, path in PREDICTION_FIELDS_CONFIG.items()
    }),
    'transcripts': lambda r: r.sortedTranscriptConsequences.map(
        lambda t: hl.struct(**{_to_camel_case(k): t[k] for k in [
            'amino_acids', 'biotype', 'canonical', 'codons', 'gene_id', 'hgvsc', 'hgvsp',
            'lof', 'lof_flags', 'lof_filter', 'lof_info', 'major_consequence', 'transcript_id', 'transcript_rank',
        ]})).group_by(lambda t: t.geneId),
}

class HailSearch(object):

    def __init__(self, families, previous_search_results=None, return_all_queried_families=False, user=None, sort=None):
        self.samples_by_family = defaultdict(dict)
        samples = Sample.objects.filter(is_active=True, individual__family__in=families)

        data_sources = {s.elasticsearch_index for s in samples}
        if len(data_sources) > 1:
            raise InvalidSearchException(
                f'Search is only enabled on a single data source, requested {", ".join(data_sources)}')
        self._data_source = data_sources.pop()

        for s in samples.select_related('individual__family'):
            self.samples_by_family[s.individual.family.guid][s.sample_id] = s

        self._family_individual_affected_status = {}
        self._user = user
        self._sort = sort
        self._return_all_queried_families = return_all_queried_families
        self.previous_search_results = previous_search_results or {}
        self._allowed_consequences = None
        self._allowed_consequences_secondary = None
        self._sample_table_queries = {}

        self.ht = None

    def _load_table(self, intervals=None):
        self.ht = hl.read_matrix_table(
            f'/hail_datasets/{self._data_source}.mt', _intervals=intervals, _filter_intervals=bool(intervals)
        ).rows()  # TODO read_table?

    def _sample_table(self, sample):
        return hl.read_table(f'/hail_datasets/{sample.elasticsearch_index}_samples/sample_{sample.sample_id}.ht')

    @classmethod
    def process_previous_results(cls, previous_search_results, page=1, num_results=100, load_all=False):
        # return EsSearch.process_previous_results(*args, **kwargs)
        # TODO re-enable caching at some point, but not helpful for development
        return None, {'page': page, 'num_results': num_results}

    def filter_variants(self, inheritance=None, genes=None, intervals=None, rs_ids=None, variant_ids=None, locus=None,
                        frequencies=None, pathogenicity=None, in_silico=None, annotations=None, annotations_secondary=None,
                        quality_filter=None, custom_query=None, skip_genotype_filter=False):
        has_location_filter = genes or intervals or rs_ids or variant_ids

        self._filter_custom(custom_query)

        if has_location_filter:
            self.filter_by_location(
                genes=genes, intervals=intervals, rs_ids=rs_ids, variant_ids=variant_ids, locus=locus)
        else:
            self._load_table()

        self._filter_by_frequency(frequencies, pathogenicity=pathogenicity)

        self._filter_by_in_silico(in_silico)

        quality_filter = quality_filter or {}
        if quality_filter.get('vcf_filter') is not None:
            self.ht = self.ht.filter(self.ht.filters.length() < 1)

        annotations = {k: v for k, v in (annotations or {}).items() if v}
        # new_svs = bool(annotations.pop(NEW_SV_FIELD, False))
        splice_ai = annotations.pop(SPLICE_AI_FIELD, None)
        self._allowed_consequences = sorted({ann for anns in annotations.values() for ann in anns})

        inheritance_mode = (inheritance or {}).get('mode')
        inheritance_filter = (inheritance or {}).get('filter') or {}
        if inheritance_filter.get('genotype'):
            inheritance_mode = None

        if inheritance:
            for family_guid, samples_by_id in self.samples_by_family.items():
                self._family_individual_affected_status[family_guid] = _get_family_affected_status(
                    samples_by_id, inheritance_filter)

            for family_guid, individual_affected_status in self._family_individual_affected_status.items():
                has_affected_samples = any(
                    aftd == Individual.AFFECTED_STATUS_AFFECTED for aftd in individual_affected_status.values()
                )
                if not has_affected_samples:
                    del self.samples_by_family[family_guid]

            if len(self.samples_by_family) < 1:
                raise InvalidSearchException(
                    'Inheritance based search is disabled in families with no data loaded for affected individuals')

        if inheritance_mode in {RECESSIVE, COMPOUND_HET}:
            self._filter_compound_hets(annotations_secondary, quality_filter, has_location_filter)
            if inheritance_mode == COMPOUND_HET:
                self.ht = None
                return

        self._filter_by_annotations(pathogenicity, splice_ai)

        self._annotate_filtered_genotypes(inheritance_mode, inheritance_filter, quality_filter)

    def filter_by_location(self, genes=None, intervals=None, rs_ids=None, variant_ids=None, locus=None):
        if rs_ids or variant_ids:
            raise NotImplementedError # TODO rs_ids/variant_ids, location_filter.get('excludeLocations')

        # parsed_intervals = [
        #     hl.parse_locus_interval(interval, reference_genome="GRCh38") for interval in
        #     ['{chrom}:{start}-{end}'.format(**interval) for interval in intervals or []] + [
        #         # long-term we should check project to get correct genome version
        #         'chr{chromGrch38}:{startGrch38}-chr{chromGrch38}:{endGrch38}'.format(**gene) for gene in (genes or {}).values()]
        # ]
        parsed_intervals = [
            hl.Struct(start=start, end=end)
            for start, end in [(
                '{chrom}:{start}'.format(**interval), '{chrom}:{end}'.format(**interval)
            ) for interval in intervals or []] + [(
                # long-term we should check project to get correct genome version
                'chr{chromGrch38}:{startGrch38}'.format(**gene), 'chr{chromGrch38}:{endGrch38}'.format(**gene)
            ) for gene in (genes or {}).values()]
        ]
        t = hl.expr.impute_type(parsed_intervals)
        pt = t.element_type.point_type
        logger.info(pt)

        self._load_table(intervals=parsed_intervals)

        self.ht = hl.filter_intervals(self.ht, parsed_intervals)

    def _filter_custom(self, custom_query):
        if custom_query:
            raise NotImplementedError

    def _filter_by_frequency(self, frequencies, pathogenicity=None):
        if not frequencies:
            return

        #  UI bug causes sv freq filter to be added despite no SV data
        frequencies.pop('sv_callset', None)

        clinvar_path_filters = [
            f for f in (pathogenicity or {}).get('clinvar', [])
            if f in {CLINVAR_PATH_FILTER, CLINVAR_LIKELY_PATH_FILTER}
        ]
        has_path_override = bool(clinvar_path_filters) and any(
                freqs.get('af') or 1 < PATH_FREQ_OVERRIDE_CUTOFF for freqs in frequencies.values())

        # In production: will not have callset frequency, may rename these fields
        callset_filter = frequencies.pop('callset', {}) or {}
        if callset_filter.get('af') is not None:
            callset_f = self.ht.AF <= callset_filter['af']
            if has_path_override and callset_filter['af'] < PATH_FREQ_OVERRIDE_CUTOFF:
                callset_f |= (
                        self._get_pathogenicity_filter({'clinvar': clinvar_path_filters}) &
                        (self.ht.AF <= PATH_FREQ_OVERRIDE_CUTOFF)
                )
            self.ht = self.ht.filter(callset_f)
        elif callset_filter.get('ac') is not None:
            self.ht = self.ht.filter(self.ht.AC <= callset_filter['ac'])

        for pop, freqs in sorted(frequencies.items()):
            pop_filter = None
            if freqs.get('af') is not None:
                af_field = POPULATIONS[pop].get('filter_af') or POPULATIONS[pop]['af']
                pop_filter = self.ht[pop][af_field] <= freqs['af']
                if has_path_override and freqs['af'] < PATH_FREQ_OVERRIDE_CUTOFF:
                    pop_filter |= (
                            self._get_pathogenicity_filter({'clinvar': clinvar_path_filters}) &
                            (self.ht[pop][af_field] <= PATH_FREQ_OVERRIDE_CUTOFF)
                    )
            elif freqs.get('ac') is not None:
                ac_field = POPULATIONS[pop]['ac']
                if ac_field:
                    pop_filter = self.ht[pop][ac_field] <= freqs['ac']

            if freqs.get('hh') is not None:
                hom_field = POPULATIONS[pop]['hom']
                hemi_field = POPULATIONS[pop]['hemi']
                if hom_field:
                    hh_filter = self.ht[pop][hom_field] <= freqs['hh']
                    if pop_filter is None:
                        pop_filter = hh_filter
                    else:
                        pop_filter &= hh_filter
                if hemi_field:
                    hh_filter = self.ht[pop][hemi_field] <= freqs['hh']
                    if pop_filter is None:
                        pop_filter = hh_filter
                    else:
                        pop_filter &= hh_filter

            if pop_filter is not None:
                self.ht = self.ht.filter(hl.is_missing(self.ht[pop]) | pop_filter)

    def _filter_by_in_silico(self, in_silico_filters):
        in_silico_filters = {k: v for k, v in (in_silico_filters or {}).items() if v is not None and len(v) != 0}
        if not in_silico_filters:
            return

        in_silico_q = None
        missing_in_silico_q = None
        for in_silico, value in in_silico_filters.items():
            ht_value = self._get_in_silico_ht_field(in_silico)
            try:
                score_filter = ht_value >= float(value)
            except ValueError:
                score_filter = ht_value.startswith(value)

            if in_silico_q is None:
                in_silico_q = score_filter
            else:
                in_silico_q |= score_filter

            missing_score_filter = hl.is_missing(ht_value)
            if missing_in_silico_q is None:
                missing_in_silico_q = missing_score_filter
            else:
                missing_in_silico_q &= missing_score_filter

        self.ht = self.ht.filter(in_silico_q | missing_in_silico_q)

    def _get_in_silico_ht_field(self, in_silico):
        score_path = PREDICTION_FIELDS_CONFIG[in_silico]
        return self.ht[score_path[0]][score_path[1]]

    def _filter_by_annotations(self, pathogenicity, splice_ai):
        annotation_filters = []
        pathogenicity_filter = self._get_pathogenicity_filter(pathogenicity)
        if pathogenicity_filter is not None:
            annotation_filters.append(pathogenicity_filter)
        if splice_ai:
            annotation_filters.append(self._get_in_silico_ht_field(SPLICE_AI_FIELD) >= float(splice_ai))
        if self._allowed_consequences:
            annotation_filters.append(self._get_filtered_transcript_consequences(self._allowed_consequences))

        if not annotation_filters:
            return
        annotation_filter = annotation_filters[0]
        for af in annotation_filters[1:]:
            annotation_filter |= af

        self.ht = self.ht.filter(annotation_filter)

    def _get_filtered_transcript_consequences(self, allowed_consequences):
        allowed_consequences_set = hl.set(allowed_consequences)
        consequence_terms = self.ht.sortedTranscriptConsequences.flatmap(lambda tc: tc.consequence_terms)
        return consequence_terms.any(lambda ct: allowed_consequences_set.contains(ct))

    def _get_pathogenicity_filter(self, pathogenicity):
        pathogenicity = pathogenicity or {}
        clinvar_filters = pathogenicity.get('clinvar', [])
        hgmd_filters = pathogenicity.get('hgmd', [])

        pathogenicity_filter = None
        clinvar_clinical_significance_terms = set()
        for clinvar_filter in clinvar_filters:
            clinvar_clinical_significance_terms.update(CLINVAR_SIGNFICANCE_MAP.get(clinvar_filter, []))
        if clinvar_clinical_significance_terms:
            allowed_significances = hl.set(clinvar_clinical_significance_terms)
            pathogenicity_filter = allowed_significances.contains(self.ht.clinvar.clinical_significance)

        hgmd_classes = set()
        for hgmd_filter in hgmd_filters:
            hgmd_classes.update(HGMD_CLASS_MAP.get(hgmd_filter, []))
        if hgmd_classes:
            allowed_classes = hl.set(hgmd_classes)
            hgmd_filter = allowed_classes.contains(self.ht.hgmd['class'])
            pathogenicity_filter = hgmd_filter if pathogenicity_filter is None else pathogenicity_filter | hgmd_filter

        return pathogenicity_filter

    def _annotate_filtered_genotypes(self, inheritance_mode, inheritance_filter, quality_filter):
        self.ht = self.ht.join(self._filter_by_genotype(inheritance_mode, inheritance_filter, quality_filter))

    def _filter_by_genotype(self, inheritance_mode, inheritance_filter, quality_filter):
        if inheritance_mode == ANY_AFFECTED:
            inheritance_filter = None
        elif inheritance_mode:
            inheritance_filter.update(INHERITANCE_FILTERS[inheritance_mode])

        if inheritance_filter and list(inheritance_filter.keys()) == ['affected']:
            raise InvalidSearchException('Inheritance must be specified if custom affected status is set')

        family_guids = sorted(self.samples_by_family.keys())
        family_hts = [
            self._get_filtered_family_table(family_guid, inheritance_mode, inheritance_filter, quality_filter)
            for family_guid in family_guids
        ]

        genotype_ht = family_hts[0]
        for family_ht in family_hts[1:]:
            genotype_ht = genotype_ht.join(family_ht, how='outer')
        genotype_ht = genotype_ht.rename({'genotypes': 'genotypes_0'})

        return genotype_ht.annotate(
            familyGuids=hl.array([
                hl.if_else(hl.is_defined(genotype_ht[f'genotypes_{i}']), family_guid, hl.missing(hl.tstr))
                for i, family_guid in enumerate(family_guids)
            ]).filter(lambda x: hl.is_defined(x)),
            genotypes=hl.array([
                genotype_ht[f'genotypes_{i}'] for i in range(len(family_guids))
            ]).flatmap(lambda x: x).filter(lambda x: hl.is_defined(x)).group_by(lambda x: x.individualGuid).map_values(lambda x: x[0]),
        ).select(*GENOTYPE_FIELDS)


    def _get_filtered_family_table(self, family_guid, inheritance_mode, inheritance_filter, quality_filter):
        samples = list(self.samples_by_family[family_guid].values())
        sample_tables = [self._sample_table(sample).select_globals() for sample in samples]

        affected_status = self._family_individual_affected_status.get(family_guid)
        individual_genotype_filter = (inheritance_filter or {}).get('genotype') or {}

        family_ht = None
        for i, sample_ht in enumerate(sample_tables):
            if quality_filter.get('min_gq'):
                sample_ht = sample_ht.filter(sample_ht.GQ > quality_filter['min_gq'])
            # TODO ab filter

            if inheritance_filter:
                individual = samples[i].individual
                affected = affected_status[individual.guid]
                genotype = individual_genotype_filter.get(individual.guid) or inheritance_filter.get(affected)
                sample_ht = self._sample_inheritance_ht(sample_ht, inheritance_mode, individual, affected, genotype)

            if family_ht is None:
                family_ht = sample_ht
            else:
                family_ht = family_ht.join(sample_ht)

        family_ht = family_ht.rename({'GT': 'GT_0', 'GQ': 'GQ_0'})

        # Filter if any matching genotypes for any affected or any inheritance search
        if not inheritance_filter:
            non_ref_sample_indices = [
                i for i, sample in enumerate(samples)
                if affected_status[sample.individual.guid] == Individual.AFFECTED_STATUS_AFFECTED
            ] if inheritance_mode == ANY_AFFECTED else range(len(samples))
            if not non_ref_sample_indices:
                raise InvalidSearchException('At least one affected individual must be included in "Any Affected" search')

            q = family_ht[f'GT_{non_ref_sample_indices[0]}'].is_non_ref()
            for i in non_ref_sample_indices[1:]:
                q |= family_ht[f'GT_{i}'].is_non_ref()

            family_ht = family_ht.filter(q)

        return family_ht.annotate(
            genotypes=hl.array([hl.struct(
                individualGuid=hl.literal(sample.individual.guid),
                sampleId=hl.literal(sample.sample_id),
                numAlt=family_ht[f'GT_{i}'].n_alt_alleles(),
                gq=family_ht[f'GQ_{i}'],
                # TODO ab
            ) for i, sample in enumerate(samples)])).select('genotypes')


    @staticmethod
    def _sample_inheritance_ht(sample_ht, inheritance_mode, individual, affected, genotype):
        gt_filter = GENOTYPE_QUERY_MAP[genotype](sample_ht.GT)

        x_sample_ht = None
        if inheritance_mode in {X_LINKED_RECESSIVE, RECESSIVE}:
            x_sample_ht = hl.filter_intervals(
                sample_ht, [hl.parse_locus_interval('chrX', reference_genome='GRCh38')])
            if affected == Individual.AFFECTED_STATUS_UNAFFECTED and individual.sex == Individual.SEX_MALE:
                genotype = REF_REF

            x_gt_filter = GENOTYPE_QUERY_MAP[genotype](x_sample_ht.GT)
            x_sample_ht = x_sample_ht.filter(x_gt_filter)
            if inheritance_mode == X_LINKED_RECESSIVE:
                return x_sample_ht

        sample_ht = sample_ht.filter(gt_filter)

        if x_sample_ht:
            sample_ht = sample_ht.join(x_sample_ht, how='outer')

        return sample_ht

    def _filter_compound_hets(self, annotations_secondary, quality_filter, has_location_filter):
        if not self._allowed_consequences:
            from seqr.utils.elasticsearch.utils import InvalidSearchException
            raise InvalidSearchException('Annotations must be specified to search for compound heterozygous variants')

        if not has_location_filter and any(len(family_samples_by_id) > MAX_NO_LOCATION_COMP_HET_FAMILIES
                                           for family_samples_by_id in self.samples_by_family_index.values()):
            from seqr.utils.elasticsearch.utils import InvalidSearchException
            raise InvalidSearchException(
                'Location must be specified to search for compound heterozygous variants across many families')

        comp_het_consequences = set(self._allowed_consequences)
        if annotations_secondary:
            self._allowed_consequences_secondary = sorted({ann for anns in annotations_secondary.values() for ann in anns})
            comp_het_consequences.update(self._allowed_consequences_secondary)

        comp_het_ht = self.ht.filter(self._get_filtered_transcript_consequences(comp_het_consequences))
        comp_het_ht = comp_het_ht.join(self._filter_by_genotype(
            inheritance_mode=COMPOUND_HET, inheritance_filter={}, quality_filter=quality_filter,
        ))

        # TODO modify query - get multiple hits within a single gene and ideally return grouped by gene
        raise NotImplementedError

    def search(self, page=1, num_results=100):
        if not self.ht:
            raise InvalidSearchException('Filters must be applied before search')

        total_results = self.ht.count()

        rows = self.ht.annotate_globals(gv=hl.eval(self.ht.genomeVersion)).drop('genomeVersion') # prevents name collision with global
        rows = rows.annotate(**{k: v(rows) for k, v in ANNOTATION_FIELDS.items()})
        rows = rows.key_by('variantId')
        rows = rows.select(*CORE_FIELDS, *GENOTYPE_FIELDS, *ANNOTATION_FIELDS.keys())

        self.previous_search_results['total_results'] = total_results
        logger.info(f'Total hits: {total_results}')

        # TODO page, self._sort
        collected = rows.take(num_results)
        hail_results = [_json_serialize(dict(row)) for row in collected]

        # TODO potentially post-process compound hets
        return hail_results

# For production: should use custom json serializer
def _json_serialize(result):
    if isinstance(result, list):
        return [_json_serialize(o) for o in result]

    if isinstance(result, hl.Struct) or isinstance(result, hl.utils.frozendict):
        result = dict(result)

    if isinstance(result, dict):
        return {k: _json_serialize(v)  for k, v in result.items()}

    return result
