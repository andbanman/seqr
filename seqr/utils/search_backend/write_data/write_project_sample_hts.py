import argparse
import hail as hl

def write_project_sample_hts(file, project):
    subset_ht = hl.import_table(f'gs://seqr-project-subsets/{project}_ids.txt', key='s')

    mt =  hl.read_matrix_table( f'gs://hail-backend-datasets/{file}.mt').select_globals().select_rows()
    mt = mt.semi_join_cols(subset_ht)
    mt = mt.filter_rows(hl.agg.any(mt.GT.is_non_ref()))

    mt = mt.annotate_entries(AB=hl.if_else(mt.AD.length() > 1, hl.float(mt.AD[1] / hl.sum(mt.AD)), hl.missing(hl.tfloat)))
    mt = mt.select_entries('AB', 'AD', 'DP', 'GQ', 'GT', 'PL')
    hl.experimental.export_entries_by_col(
        mt,  f'gs://hail-backend-datasets/{file}__samples/{project}', use_string_key_as_file_name=True, header_json_in_file=False)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('file')
    p.add_argument('project')
    args = p.parse_args()

    write_project_sample_hts(args.file, args.project)