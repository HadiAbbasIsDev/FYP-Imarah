"""Make editable Word assignment documents from the text in the sources folder.

Copyright (c) 2026 Imarah.tech. All rights reserved.
Uses standard Python and Ubuntu's SVG renderer; no project packages are changed.
"""

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'documents'
BLACK = '000000'
NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')


def run(text, bold=False, color=None, size=None):
    props = ('<w:b/>' if bold else '')
    if color:
        props += f'<w:color w:val="{color}"/>'
    if size:
        props += f'<w:sz w:val="{size}"/>'
    return f'<w:r><w:rPr>{props}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def paragraph(text='', style='Normal', extra='', content=None):
    return (f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{extra}</w:pPr>'
            f'{run(text) if content is None else content}</w:p>')


def table(rows):
    count = len(rows[0])
    widths = [int(9600 / count)] * count
    if count == 2:
        widths = [3400, 6200]
    elif count >= 4:
        widths = [2600] + [int(7000 / (count - 1))] * (count - 1)
    grid = ''.join(f'<w:gridCol w:w="{width}"/>' for width in widths)
    body = ''
    for idx, row in enumerate(rows):
        cells = ''
        for col, cell in enumerate(row):
            shade = BLACK if idx == 0 else ('F2F2F2' if idx % 2 else 'FFFFFF')
            value = run(cell, bold=idx == 0, color='FFFFFF' if idx == 0 else BLACK, size=18)
            cells += (f'<w:tc><w:tcPr><w:tcW w:w="{widths[col]}" w:type="dxa"/>'
                      f'<w:shd w:fill="{shade}"/><w:vAlign w:val="center"/></w:tcPr>'
                      + paragraph(style='TableText', content=value) + '</w:tc>')
        body += ('<w:tr><w:trPr><w:cantSplit/>' + ('<w:tblHeader/>' if idx == 0 else '')
                 + '</w:trPr>' + cells + '</w:tr>')
    return ('<w:tbl><w:tblPr><w:tblW w:w="9600" w:type="dxa"/>'
            '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="55" w:type="dxa"/>'
            '<w:left w:w="100" w:type="dxa"/><w:bottom w:w="55" w:type="dxa"/>'
            '<w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            f'<w:tblGrid>{grid}</w:tblGrid>{body}</w:tbl>')


def logo():
    return '''<w:p><w:pPr><w:spacing w:after="420"/></w:pPr><w:r><w:drawing>
    <wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
    <wp:extent cx="914400" cy="914400"/><wp:docPr id="1" name="Imarah.tech logo" descr="Imarah building mark"/>
    <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
    <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
    <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
    <pic:nvPicPr><pic:cNvPr id="0" name="icon.png"/><pic:cNvPicPr/></pic:nvPicPr>
    <pic:blipFill><a:blip r:embed="logo"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
    <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="914400" cy="914400"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>
    </a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'''


def styles():
    return f'''<w:styles {NS}>
    <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Liberation Sans" w:hAnsi="Liberation Sans"/>
    <w:sz w:val="21"/><w:color w:val="000000"/><w:lang w:val="en-GB"/></w:rPr></w:rPrDefault>
    <w:pPrDefault><w:pPr><w:spacing w:after="80" w:line="252" w:lineRule="auto"/>
    <w:widowControl/></w:pPr></w:pPrDefault></w:docDefaults>
    <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
    <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/>
    <w:pPr><w:keepNext/><w:spacing w:before="0" w:after="180"/><w:outlineLvl w:val="0"/></w:pPr>
    <w:rPr><w:b/><w:color w:val="{BLACK}"/><w:sz w:val="34"/></w:rPr></w:style>
    <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/>
    <w:pPr><w:keepNext/><w:spacing w:before="130" w:after="70"/><w:outlineLvl w:val="1"/></w:pPr>
    <w:rPr><w:b/><w:color w:val="{BLACK}"/><w:sz w:val="24"/></w:rPr></w:style>
    <w:style w:type="paragraph" w:styleId="TableText"><w:name w:val="Table Text"/>
    <w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:sz w:val="18"/></w:rPr></w:style>
    <w:style w:type="paragraph" w:styleId="Small"><w:name w:val="Small"/><w:basedOn w:val="Normal"/>
    <w:pPr><w:spacing w:after="100" w:line="240" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:sz w:val="18"/><w:color w:val="000000"/></w:rPr></w:style>
    </w:styles>'''


def make_doc(kind, title, subtitle, number, png):
    text = (ROOT / 'sources' / f'{kind}.md').read_text()
    assert '\u2014' not in text, 'Avoid em dashes in assignment documents.'
    body = logo()
    body += paragraph(content=run('IMARAH.TECH', bold=True, color=BLACK, size=44))
    body += paragraph(f'DOCUMENT {number:02d} OF 03  |  PPIT ASSIGNMENT 1', style='Small')
    body += paragraph(content=run(title, bold=True, color=BLACK, size=52),
                      extra='<w:spacing w:before="380" w:after="180"/>')
    body += paragraph(subtitle)
    body += paragraph('Proposed company: Imarah Technologies (Private) Limited',
                      extra='<w:spacing w:before="260" w:after="260"/>')
    body += table([['Prepared by', 'Student registration'], ['Hadi Abbas', '23K-0927'],
                   ['Ayaan Moeen', '23I-0124'], ['Saad Hussain', '23K-0705']])
    body += paragraph('BS in CS/AI | Department of CS/AI', extra='<w:spacing w:before="260"/>')
    body += paragraph('FAST National University, Karachi Campus')
    body += paragraph('Submission date: 27 September 2026')
    body += paragraph('Academic startup proposal | Version 1.0', style='Small')
    body += paragraph('Based on the Imarah.tech final year project. Proposed ownership, '
                      'appointments and financial figures are identified as assumptions. '
                      'No incorporation, signed agreement or funding receipt is claimed.',
                      style='Small', extra='<w:spacing w:before="380"/>')
    relations = [
        ('styles', 'styles', 'styles.xml', False),
        ('header', 'header', 'header1.xml', False),
        ('footer', 'footer', 'footer1.xml', False),
        ('logo', 'image', 'media/icon.png', False),
    ]
    page_break = True
    reference_section = False
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if line == '[PAGE]':
            page_break = True
            continue
        if line.startswith('|'):
            rows = [[cell.strip() for cell in line.strip('|').split('|')]]
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([cell.strip() for cell in lines[i].strip().strip('|').split('|')])
                i += 1
            body += table(rows)
            body += paragraph('', style='Small', extra='<w:spacing w:after="20"/>')
            continue
        extra = '<w:pageBreakBefore/>' if page_break else ''
        page_break = False
        if line.startswith('# '):
            reference_section = False
            body += paragraph(line[2:], 'Heading1', extra)
        elif line.startswith('## '):
            reference_section = line[3:] in {'References', 'Basis of preparation', 'References and evidence notes'}
            body += paragraph(line[3:], 'Heading2', extra)
        elif line.startswith('https://'):
            rid = f'url{len(relations)}'
            relations.append((rid, 'hyperlink', line, True))
            label = 'Source: ' + line.split('/')[2] + ' (open reference)'
            body += paragraph(style='Small', content=f'<w:hyperlink r:id="{rid}">'
                              + run(label, color=BLACK, size=18) + '</w:hyperlink>')
        elif line.startswith('- '):
            body += paragraph('• ' + line[2:], extra=extra + '<w:ind w:left="220" w:hanging="220"/>')
        else:
            body += paragraph(line, style='Small' if reference_section else 'Normal', extra=extra)
    body += ('<w:sectPr><w:headerReference w:type="default" r:id="header"/>'
             '<w:footerReference w:type="default" r:id="footer"/>'
             '<w:pgSz w:w="11906" w:h="16838"/>'
             '<w:pgMar w:top="1050" w:right="1153" w:bottom="1000" w:left="1153" '
             'w:header="470" w:footer="450"/></w:sectPr>')
    rel_xml = ''.join(f'<Relationship Id="{rid}" '
                      f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/{rtype}" '
                      f'Target="{escape(target, {chr(34): "&quot;"})}"'
                      + (' TargetMode="External"' if external else '') + '/>'
                      for rid, rtype, target, external in relations)
    header = paragraph('IMARAH.TECH  |  ' + title.upper(), 'Small',
                       '<w:pBdr><w:bottom w:val="single" w:sz="6" w:color="000000" w:space="8"/></w:pBdr>')
    footer = paragraph(style='Small', content=run('Academic proposal  •  27 September 2026', size=16)
                       + '<w:r><w:tab/></w:r>' + run('Page ', size=16)
                       + '<w:fldSimple w:instr="PAGE"><w:r><w:t>1</w:t></w:r></w:fldSimple>',
                       extra='<w:tabs><w:tab w:val="right" w:pos="9600"/></w:tabs>')
    overrides = ''.join(f'<Override PartName="/word/{name}.xml" '
                         f'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.{ctype}+xml"/>'
                         for name, ctype in [('document', 'document.main'), ('styles', 'styles'),
                                             ('header1', 'header'), ('footer1', 'footer')])
    files = {
        '[Content_Types].xml': '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="png" ContentType="image/png"/>' + overrides + '</Types>',
        '_rels/.rels': '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="document" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/></Relationships>',
        'word/document.xml': f'<w:document {NS}><w:body>{body}</w:body></w:document>',
        'word/styles.xml': styles(),
        'word/header1.xml': f'<w:hdr {NS}>{header}</w:hdr>',
        'word/footer1.xml': f'<w:ftr {NS}>{footer}</w:ftr>',
        'word/_rels/document.xml.rels': '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + rel_xml + '</Relationships>',
    }
    path = OUTPUT / f'23K-0927_23I-0124_23K-0705_Imarah_{kind}.docx'
    with ZipFile(path, 'w', ZIP_DEFLATED) as archive:
        for name, value in files.items():
            archive.writestr(name, '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + value)
        archive.writestr('word/media/icon.png', png)
    print(path)


def main():
    # Use the existing vector mark without changing the original file.
    import io
    import cairo
    import gi
    gi.require_version('Rsvg', '2.0')
    from gi.repository import Rsvg

    OUTPUT.mkdir(exist_ok=True)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 512, 512)
    context = cairo.Context(surface)
    svg = (ROOT.parent / 'frontend/public/icon.svg').read_text()
    svg = svg.replace('#183e35', '#000000').replace('#f1efe3', '#ffffff')
    icon = Rsvg.Handle.new_from_data(svg.encode())
    viewport = Rsvg.Rectangle()
    viewport.x = viewport.y = 0
    viewport.width = viewport.height = 512
    icon.render_document(context, viewport)
    png = io.BytesIO()
    surface.write_to_png(png)
    for number, (kind, title, subtitle) in enumerate([
        ('MOA', 'Memorandum of Association', 'Company identity, purpose and proposed ownership'),
        ('AOA', 'Articles of Association', 'Management, decision-making and internal responsibilities'),
        ('BusinessPlan', 'Business Plan', 'From the inspection prototype to a proposed service'),
    ], start=1):
        make_doc(kind, title, subtitle, number, png.getvalue())


if __name__ == '__main__':
    main()
