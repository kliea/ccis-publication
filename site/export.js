/* Excel and PDF downloads for the rows currently on screen. */
(function () {
  const COLUMNS = [
    ["No.", (row) => String(row.number)],
    ["Author/s", (row) => row.authors.map((author) => author.name).join(", ")],
    ["Title", (row) => row.title || ""],
    ["Journal / Conference", (row) => row.venue || ""],
    ["Sponsor / Publisher", (row) => row.sponsor || ""],
    ["Database", () => ""],
    ["Indexing", (row) => (row.indexes || []).map((id) => ({
      scopus: "Scopus",
      wos: "Web of Science",
      aci: "Asian Citation Index"
    }[id] || "")).filter(Boolean).join("; ")],
    ["Ranking / JIF", () => ""],
    ["ISSN / ISBN", (row) => row.issn || ""],
    ["Status", () => "Published"],
    ["Date", (row) => row.date || ""],
    ["Publication Charge", (row) => row.charge || ""],
    ["Link / DOI", (row) => row.doi || ""],
    ["SDG", (row) => (row.sdgs || []).map((goal) => goal.number + " " + goal.name).join("; ")]
  ];

  const WIDTHS = [32, 130, 170, 115, 120, 42, 42, 48, 62, 52, 58, 52, 130, 90];

  function selectedYear() {
    const value = document.getElementById("year").value;
    return value ? Number(value) : null;
  }

  function visibleRows(allRows) {
    const goal = document.getElementById("sdg").value;
    const year = selectedYear();
    const list = allRows.flatMap((row, index) => {
      const goals = row.sdgs || [];
      const yearOk = year === null || row.year === year;
      const goalOk = !goal || goals.some((item) => String(item.number) === goal);
      return yearOk && goalOk ? [Object.assign({ number: index + 1 }, row)] : [];
    });
    return window.catalogSortRows ? window.catalogSortRows(list) : list;
  }

  function fileStem() {
    const year = selectedYear();
    const years = year === null ? "2023-2026" : String(year);
    const goal = document.getElementById("sdg").value;
    return "publication-catalog-" + years + (goal ? "-sdg-" + goal : "");
  }

  function subtitle() {
    return document.getElementById("count").textContent;
  }

  function xml(value) {
    return String(value).replace(/[&<>"']/g, (ch) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&apos;"
    }[ch]));
  }

  function buildExcel(exported) {
    const header = COLUMNS.map(([label]) =>
      '<Cell ss:StyleID="h"><Data ss:Type="String">' + xml(label) + "</Data></Cell>"
    ).join("");
    const body = exported.map((row) => {
      const cells = COLUMNS.map(([label, value], index) => {
        const text = value(row);
        const link = label === "Link / DOI" && text
          ? ' ss:HRef="' + xml(text) + '"'
          : "";
        return '<Cell ss:StyleID="c"' + link + '><Data ss:Type="String">' + xml(text) + "</Data></Cell>";
      });
      return "<Row>" + cells.join("") + "</Row>";
    }).join("");
    return '<?xml version="1.0" encoding="UTF-8"?>\n'
      + '<?mso-application progid="Excel.Sheet"?>\n'
      + '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">\n'
      + '<Styles>'
      + '<Style ss:ID="h"><Font ss:Bold="1"/><Interior ss:Color="#EBE4D6" ss:Pattern="Solid"/></Style>'
      + '<Style ss:ID="c"><Alignment ss:Vertical="Top" ss:WrapText="1"/></Style>'
      + '</Styles>'
      + '<Worksheet ss:Name="Publications"><Table>\n'
      + "<Row>" + header + "</Row>\n"
      + body
      + "\n</Table></Worksheet></Workbook>\n";
  }

  const WINANSI = {
    0x2013: 0x96,
    0x2014: 0x97,
    0x2018: 0x91,
    0x2019: 0x92,
    0x201c: 0x93,
    0x201d: 0x94,
    0x2022: 0x95,
    0x2026: 0x85,
    0x00a0: 0xa0
  };

  function pdfString(text) {
    let out = "";
    for (const ch of String(text)) {
      let code = ch.codePointAt(0);
      if (WINANSI[code]) code = WINANSI[code];
      if (code === 0x5c || code === 0x28 || code === 0x29) {
        out += "\\" + String.fromCharCode(code);
        continue;
      }
      if (code >= 32 && code <= 126) out += String.fromCharCode(code);
      else if (code >= 160 && code <= 255) out += "\\" + code.toString(8).padStart(3, "0");
      else if (code >= 127 && code <= 159) out += "\\" + code.toString(8).padStart(3, "0");
      else out += "?";
    }
    return out;
  }

  function wrap(text, width, size) {
    const max = Math.max(4, Math.floor((width - 4) / (size * 0.48)));
    const words = String(text || "").split(/\s+/).filter(Boolean);
    if (!words.length) return [""];
    const lines = [];
    let line = "";
    words.forEach((word) => {
      const parts = [];
      let rest = word;
      while (rest.length > max) {
        parts.push(rest.slice(0, max));
        rest = rest.slice(max);
      }
      parts.push(rest);
      parts.forEach((part) => {
        const next = line ? line + " " + part : part;
        if (next.length > max && line) {
          lines.push(line);
          line = part;
        } else {
          line = next;
        }
      });
    });
    if (line) lines.push(line);
    return lines;
  }

  function buildPdf(exported, heading) {
    const pageWidth = 1191;
    const pageHeight = 842;
    const margin = 24;
    const size = 7;
    const leading = 9;
    const columns = COLUMNS.map(([label]) => label);
    const headerLines = columns.map((label, index) => wrap(label, WIDTHS[index], size));
    const headerHeight = Math.max(...headerLines.map((lines) => lines.length)) * leading + 6;
    const pages = [];
    let commands = [];
    let y = pageHeight - margin;
    let fresh = true;

    function text(x, baseline, value, fontSize) {
      commands.push(
        "BT /F1 " + fontSize + " Tf 1 0 0 1 " + x.toFixed(1) + " " + baseline.toFixed(1)
        + " Tm (" + pdfString(value) + ") Tj ET"
      );
    }

    function startPage() {
      commands = [];
      y = pageHeight - margin;
      fresh = true;
      text(margin, y - 11, "Publication catalog", 12);
      y -= 16;
      text(margin, y - 8, heading, 8);
      y -= 16;
      paintHeader();
    }

    function paintHeader() {
      let x = margin;
      commands.push("0.922 0.894 0.839 rg");
      commands.push(margin + " " + (y - headerHeight).toFixed(1) + " " + WIDTHS.reduce((sum, width) => sum + width, 0) + " " + headerHeight + " re f");
      commands.push("0 0 0 rg");
      headerLines.forEach((lines, index) => {
        lines.forEach((line, lineIndex) => {
          text(x + 2, y - 10 - lineIndex * leading, line, size);
        });
        x += WIDTHS[index];
      });
      y -= headerHeight;
    }

    function paintRow(cellLines) {
      const rowHeight = Math.max(...cellLines.map((lines) => lines.length)) * leading + 5;
      if (!fresh && y - rowHeight < margin) {
        pages.push(commands.join("\n"));
        startPage();
      }
      fresh = false;
      let x = margin;
      commands.push("0.85 0.82 0.77 RG 0.4 w");
      commands.push(margin + " " + (y - rowHeight).toFixed(1) + " m " + (margin + WIDTHS.reduce((sum, width) => sum + width, 0)) + " " + (y - rowHeight).toFixed(1) + " l S");
      commands.push("0 0 0 RG 0 0 0 rg");
      cellLines.forEach((lines, index) => {
        lines.forEach((line, lineIndex) => {
          text(x + 2, y - 9 - lineIndex * leading, line, size);
        });
        x += WIDTHS[index];
      });
      y -= rowHeight;
    }

    startPage();
    if (!exported.length) {
      text(margin, y - 12, "No publications for this filter.", 9);
    }
    exported.forEach((row) => {
      const cellLines = COLUMNS.map(([, value], index) => wrap(value(row), WIDTHS[index], size));
      paintRow(cellLines);
    });
    pages.push(commands.join("\n"));

    const pageIds = pages.map((_, index) => 4 + index * 2);
    const catalog = "<< /Type /Catalog /Pages 2 0 R >>";
    const pageTree = "<< /Type /Pages /Count " + pages.length + " /Kids [" + pageIds.map((id) => id + " 0 R").join(" ") + "] >>";
    const font = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>";
    const ordered = [catalog, pageTree, font];
    pages.forEach((stream, index) => {
      const pageId = pageIds[index];
      const contentId = pageId + 1;
      ordered.push(
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 " + pageWidth + " " + pageHeight + "]"
        + " /Contents " + contentId + " 0 R /Resources << /Font << /F1 3 0 R >> >> >>"
      );
      ordered.push("<< /Length " + stream.length + " >>\nstream\n" + stream + "\nendstream");
    });
    let file = "%PDF-1.4\n";
    const offsets = [0];
    ordered.forEach((entry, index) => {
      offsets.push(file.length);
      file += (index + 1) + " 0 obj\n" + entry + "\nendobj\n";
    });
    const xref = file.length;
    file += "xref\n0 " + (ordered.length + 1) + "\n";
    file += "0000000000 65535 f \n";
    offsets.slice(1).forEach((offset) => {
      file += String(offset).padStart(10, "0") + " 00000 n \n";
    });
    file += "trailer\n<< /Size " + (ordered.length + 1) + " /Root 1 0 R >>\n";
    file += "startxref\n" + xref + "\n%%EOF\n";
    const bytes = new Uint8Array(file.length);
    for (let i = 0; i < file.length; i += 1) bytes[i] = file.charCodeAt(i) & 255;
    return bytes;
  }

  function download(data, name, type) {
    const blob = new Blob([data], { type: type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function excel(allRows) {
    download(buildExcel(visibleRows(allRows)), fileStem() + ".xls", "application/vnd.ms-excel");
  }

  function pdf(allRows) {
    download(buildPdf(visibleRows(allRows), subtitle()), fileStem() + ".pdf", "application/pdf");
  }

  window.CatalogExport = { excel: excel, pdf: pdf, buildExcel: buildExcel, buildPdf: buildPdf, visibleRows: visibleRows };
})();
