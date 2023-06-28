
import yaml

def get_sssom_tsv_headers(tsv_file):
    header_lines = []
    line = tsv_file.readline()
    while line.startswith('#'):
        header_lines.append(line[1:])
        line = tsv_file.readline()
    yaml_header = yaml.safe_load('\n'.join(header_lines))

    column_headers = line.strip().split('\t')

    return yaml_header,column_headers

