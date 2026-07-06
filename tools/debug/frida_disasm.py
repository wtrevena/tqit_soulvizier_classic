"""One-shot: disassemble the three sites that navigate the region-manager global
(0x103743f0) so the sweep uses the REAL pointer path. Attach, disasm, print, exit."""
import sys, time, json
import frida

SITES = {
    "GetConnectedRegion lookup tail (0x20643a)": (0x20642a, 46),
}
JS = r"""
const SITES = __SITES__;
const base = Process.getModuleByName('Engine.dll').base;
const out = [];
for (const [name, spec] of Object.entries(SITES)) {
  out.push('==== ' + name + ' ====');
  let addr = base.add(spec[0]);
  for (let i = 0; i < spec[1]; i++) {
    try {
      const ins = Instruction.parse(addr);
      // rebase display to image-base 0x10000000 for doc cross-ref
      const rva = addr.sub(base).toInt32() >>> 0;
      out.push('  1' + ('000000' + rva.toString(16)).slice(-7) + '  ' + ins.mnemonic + ' ' + ins.opStr);
      addr = ins.next;
    } catch (e) { out.push('  <parse fail: ' + e + '>'); break; }
  }
}
send({t:'disasm', text: out.join('\n')});
"""
JS = JS.replace('__SITES__', json.dumps({k: list(v) for k, v in SITES.items()}))
done = []
def on_message(msg, _):
    if msg['type'] == 'error': print('JS ERROR:', msg.get('description')); done.append(1); return
    p = msg.get('payload', {})
    if p.get('t') == 'disasm': print(p['text'], flush=True); done.append(1)
s = frida.attach("TQ.exe")
sc = s.create_script(JS); sc.on('message', on_message); sc.load()
for _ in range(100):
    if done: break
    time.sleep(0.1)
s.detach()
