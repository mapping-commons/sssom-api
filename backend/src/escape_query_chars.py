
# ported from:
# https://github.com/apache/solr/blob/d772f112032c4a8648c97d688b792ccb6459a10e/solr/solrj/src/java/org/apache/solr/client/solrj/util/ClientUtils.java#L40
# by ChatGPT
#
def escape_query_chars(s):
    sb = []
    for c in s:
        if c == '\\' or c == '+' or c == '-' or c == '!' or c == '(' or c == ')' or c == ':' or c == '^' or c == '[' or c == ']' or c == '\"' or c == '{' or c == '}' or c == '~' or c == '*' or c == '?' or c == '|' or c == '&' or c == ';' or c == '/' or c.isspace():
            sb.append('\\')
        sb.append(c)
    return ''.join(sb)
