// Real-audio test clip: `at` times come from words.txt ("Picks" 0.00, "then" 1.98).
scene({ size: [720, 1280], audio: 'audio.wav', beats: [
  { at: 0, say: 'picks a tool and acts', draw: p => write('Act', 360, 300, p, { size: 56, color: C.orange, center: true }) },
  { at: 1.98, say: 'then it looks at the result, and repeats', draw: p => write('Observe', 360, 500, p, { size: 56, color: C.pink, center: true }) },
]});
