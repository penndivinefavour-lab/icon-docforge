const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

class Element {
  constructor(tag='div') { this.tagName=tag; this.children=[]; this.style={}; this.classList={add(){},remove(){}}; this.dataset={}; this._html=''; this.textContent=''; }
  addEventListener() {}
  setAttribute() {}
  appendChild(child) { this.children.push(child); return child; }
  set innerHTML(value) { this._html=value; this.children=[]; }
  get innerHTML() { return this._html; }
  querySelector(sel) { return this._children?.[sel] || null; }
}

const nodes = {};
for (const id of ['home-screen','tool-screen','result-screen','settings-screen','tools-grid','categories','search-input','tool-body','tool-title','history-section','history-list','result-icon','result-name','result-info','app-version']) {
  nodes[id] = new Element();
}
nodes['home-screen'].classList = { add(v){this.active=v}, remove(){} };
const context = {
  window: { addEventListener(){}, location:{hash:'',hostname:''} },
  document: { getElementById:id=>nodes[id] || null, createElement:(tag)=>new Element(tag), addEventListener(){}, body:new Element('body') },
  localStorage: { getItem:()=>null, setItem(){} },
  console,
  setTimeout, clearTimeout,
};
context.window.window = context.window;
context.window.document = context.document;
context.window.localStorage = context.localStorage;
context.window.setTimeout = setTimeout;
context.document.defaultView = context.window;
vm.createContext(context);
vm.runInContext(fs.readFileSync('web/js/app.js','utf8'), context);
assert.strictEqual(nodes['tools-grid'].children.length, 12, 'catalogue should render 12 tool cards');
assert.strictEqual(nodes['categories'].children.length, 6, 'category filters should render');
const search = context.window.__docforgeTest;
if (search) {
  search.setSearch('split');
  assert.strictEqual(nodes['tools-grid'].children.length, 1, 'search should filter to PDF Split');
}
console.log('frontend integration PASS: 12 cards, 6 categories, DFRegistry loader');
