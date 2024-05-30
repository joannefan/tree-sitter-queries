from tree_sitter_languages import get_language, get_parser

# helpful query references:
# https://github.com/tree-sitter/tree-sitter-html/blob/master/queries/injections.scm
# https://github.com/tree-sitter/tree-sitter-javascript/blob/master/queries/highlights.scm

script_Q = '((script_element (raw_text) @injection.content) (#set! injection.language "javascript"))'
function_call_Q = "(call_expression function: (identifier) @function) @function_call"

languageJs = get_language('javascript')
parserJs = get_parser('javascript')

languageHtml = get_language('html')
parserHtml = get_parser('html')

# helpers
def node_source_code(tsnode, source_code):
    start_byte = tsnode.start_byte
    end_byte = tsnode.end_byte
    return source_code[start_byte:end_byte]

# recursively prints the abstract syntax tree
def print_named_node(node, indent=0):
    if node.is_named:
        print('   ' * indent + node.type)
        for child in node.children:
            print_named_node(child, indent + 1)

def parse_tree(parser, source_code):
    return parser.parse(bytes(source_code, "utf8"))

def parse_html(source_code):
    tree = parse_tree(parserHtml, source_code)
    query = languageHtml.query(script_Q)
    captures = query.captures(tree.root_node)

    for capture in captures:
        js_code = node_source_code(capture[0], source_code)
        parse_js(js_code)

def parse_js(js_code):
    tree = parse_tree(parserJs, js_code)
    query = languageJs.query(function_call_Q)
    captures = query.captures(tree.root_node)

    print("\n<-- function calls in the javascript code:")
    for capture in captures:
        # uncomment this to print just the function name
        # if capture[0].type == 'identifier':
        #     print("\nname of called function:")
        #     print(node_source_code(capture[0], js_code))

        if capture[0].type == 'call_expression':
            print("\n<-- complete function call:")
            print(node_source_code(capture[0], js_code))


if __name__ == "__main__":
    with open("test.html", 'r') as file:
        source_code = file.read()
        parse_html(source_code)
