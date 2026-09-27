# Tool Adapters

Adapters wrap external tools (Nmap, ZAP, etc) into the NyxOS data model.

Adapter interface:
    name, version, run(input) -> parsed_output

Output goes to:
    Output Parser -> Evidence -> Finding -> Asset -> Risk
