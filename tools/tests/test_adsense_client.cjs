const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('core/js/adsense.js', 'utf8');

function run(host, enabled = 'false') {
  const scripts = [], children = [];
  const section = { hidden: true, dataset: { enabled, client: 'ca-pub-1540286884381775', slot: '8395271355' } };
  const slot = { appendChild: node => children.push(node), getBoundingClientRect: () => ({ width: 728 }) };
  section.querySelector = () => slot;
  let observerCallback;
  const window = { location: { hostname: host } };
  vm.runInNewContext(source, {
    window,
    document: {
      querySelector: selector => selector === '.article-ad' ? section : null,
      createElement: tag => ({ tag, dataset: {}, style: {} }),
      head: { appendChild: script => scripts.push(script) },
      addEventListener: (name, callback) => callback(),
    },
    MutationObserver: class {
      constructor(callback) { observerCallback = callback; }
      observe() {}
      disconnect() {}
    },
  });
  return { section, children, scripts, window, observe: () => observerCallback() };
}

test('local preview never requests ads, including with production enabled', () => {
  for (const host of ['localhost', '127.0.0.1', '[::1]']) {
    const result = run(host, 'true');
    assert.equal(result.section.hidden, false);
    assert.match(result.children[0].textContent, /本機版位預覽/);
    assert.equal(result.scripts.length, 0);
    assert.equal(result.window.adsbygoogle, undefined);
  }
});

test('production stays hidden until enabled and preview domains never request ads', () => {
  for (const [host, enabled] of [['chxtravel.com', 'false'], ['www.chxtravel.com', 'false'], ['ch-travel.pages.dev', 'true']]) {
    const result = run(host, enabled);
    assert.equal(result.section.hidden, true);
    assert.equal(result.scripts.length, 0);
    assert.equal(result.children.length, 0);
  }
});

test('approved host requests one horizontal unit and hides unfilled inventory', () => {
  const result = run('chxtravel.com', 'true');
  assert.equal(result.scripts.length, 1);
  assert.equal(result.children.length, 1);
  assert.equal(result.children[0].dataset.adFormat, 'horizontal');
  assert.equal(result.children[0].dataset.fullWidthResponsive, 'false');
  assert.equal(result.window.adsbygoogle.length, 1);
  result.children[0].dataset.adStatus = 'unfilled';
  result.observe();
  assert.equal(result.section.hidden, true);
});
