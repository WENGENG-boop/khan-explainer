#!/usr/bin/env node
// Which face each script actually gets on this machine:  node tests/fonts.js
// Chrome itself reports the platform font it shaped the sample with; one outside the scene's list is the system fallback.
const path = require('path'), { pathToFileURL } = require('url');
const { chromium } = require(path.join(__dirname, '../scripts/node_modules/playwright'));
const SAMPLE = { Hebrew: 'ספר', Urdu: 'نئی کتاب', Arabic: 'كتاب', Syriac: 'ܟܬܒܐ', Devanagari: 'किताब', Bengali: 'নতুন বই', Gurmukhi: 'ਕਿਤਾਬ',
                 Gujarati: 'પુસ્તક', Tamil: 'புத்தகம்', Telugu: 'పుస్తకం', Kannada: 'ಪುಸ್ತಕ', Thai: 'หนังสือ', Kana: 'あたらしい', Hangul: '새 책', Han: '新书', Cyrillic: 'книга' };
(async () => {
  const b = await chromium.launch(), pg = await b.newPage(), cdp = await pg.context().newCDPSession(pg);
  await pg.goto(pathToFileURL(path.join(__dirname, '../scripts/board.html')).href);
  const rows = await pg.evaluate(SAMPLE => {
    const name = k => k.urdu ? 'Urdu' : (k.re.source.match(/Script=(\w+)/) || [])[1]?.replace(/^Hiragana$/, 'Kana') || '?';
    return SCRIPTS.map((k, i) => { const n = name(k), s = SAMPLE[n] || '', el = document.createElement('span');
      el.id = 'f' + i; el.style.fontFamily = k.face; el.textContent = s; document.body.append(el);
      return { script: n, id: el.id, sample: s, tried: k.face.split(',').map(f => f.replace(/"/g, '')) }; });
  }, SAMPLE);
  await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
  const { root } = await cdp.send('DOM.getDocument');
  for (const r of rows) {
    if (!r.sample) { r.uses = '-'; continue; }
    const { nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector: '#' + r.id });
    const used = (await cdp.send('CSS.getPlatformFontsForNode', { nodeId })).fonts.map(f => f.familyName);
    r.uses = used.find(f => r.tried.includes(f)) || `NONE (system fallback: ${used.join(', ')})`;
  }
  await b.close();
  rows.forEach(r => console.log(`${r.script.padEnd(11)} ${r.uses.padEnd(28)} (${r.tried.join(', ')})`));
})();
