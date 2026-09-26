const normalizeDesig = (n) => {
    let v = n.replace(/\s+/g, ' ').replace(/\s*:\s*\d{4}.*$/, '');
    v = v.replace(/(?:\s*:\s*|\s+)(Part\s*\d+[a-zA-Z]*)(?:\s*:\s*|\s+)(Sec\s*\d+[a-zA-Z]*)/gi, '($1/$2)');
    v = v.replace(/(?:\s*:\s*|\s+)(Part\s*\d+[a-zA-Z]*)/gi, '($1)');
    v = v.replace(/(?:\s*:\s*|\s+)(Sec\s*\d+[a-zA-Z]*)/gi, '($1)');
    return v.replace(/\(\s*(Part|Sec)\s+/gi, '($1 ').replace(/\s*\)/g, ')').replace(/([^\s])\(/g, '$1 (').toUpperCase().trim();
};
console.log(normalizeDesig("IS 10322 : Part 5 : Sec 3"));
console.log(normalizeDesig("IS 10322 (Part 5/Sec 3):2013 Amd.2"));
console.log(normalizeDesig("IS 10322 (Part 1)"));
console.log(normalizeDesig("IS 10322 : Part 1"));
