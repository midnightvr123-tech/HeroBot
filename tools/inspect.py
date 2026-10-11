import subprocess, sys, re
jar, tag = sys.argv[1], sys.argv[2]
def javap(cls):
    return subprocess.run(["javap", "-c", "-p", "-classpath", jar, cls], capture_output=True, text=True).stdout
def methods(src):
    cur = None; out = {}
    for line in src.split("\n"):
        m = re.match(r"^  (?:[\w$<>\[\],. ]+ )?([\w$<>]+)\(([^)]*)\)[^;]*;$", line)
        if m: cur = m.group(1) + "(" + m.group(2) + ")"; out[cur] = []; continue
        if cur and ("invoke" in line or "field" in line.lower()):
            mm = re.search(r"// (Method|InterfaceMethod|Field) (\S+)", line)
            if mm: out[cur].append(mm.group(2))
    return out
lines = []
P = methods(javap("net.minecraft.world.entity.player.Player"))
for k, v in P.items():
    if k.startswith("attack(") :
        keep = [x for x in v if re.search(r"hurt|Knockback|knockback|invulnerable|Invulnerable|swing|AttackStrength|setDeltaMovement|syncVelocity|hurtMarked|sweep|crit", x)]
        lines.append(f"Player.{k}: " + " > ".join(x.split(".")[-1].split(":")[0] for x in keep))
for cls in ["net.minecraft.world.entity.Entity", "net.minecraft.world.entity.LivingEntity",
            "net.minecraft.world.entity.player.Player", "net.minecraft.server.level.ServerPlayer"]:
    M = methods(javap(cls))
    for k, v in M.items():
        hits = [x for x in v if re.search(r"invulnerableTime|InvulnerableTime", x)]
        if hits:
            lines.append(f"{cls.split('.')[-1]}.{k} uses: " + ", ".join(sorted(set(h.split('.')[-1] for h in hits))))
def fields_in(cls, prefix):
    src = javap(cls); cur=None; acc={}
    for line in src.split("\n"):
        m = re.match(r"^  (?:[\w$<>\[\],. ]+ )?([\w$<>]+)\(([^)]*)\)[^;]*;$", line)
        if m: cur = m.group(1); continue
        if cur and cur.startswith(prefix):
            mm = re.search(r"(getfield|putfield)\s.*// Field (\S+)", line)
            if mm: acc.setdefault(cur, []).append(mm.group(1)[:3]+":"+mm.group(2).split(":")[0])
    return acc
lines = [l for l in lines if "Player.attack" in l]
for cls, pre in [("net.minecraft.world.entity.LivingEntity","knockback"),("net.minecraft.server.level.ServerEntity","sendChanges"),("net.minecraft.world.entity.Entity","markHurt"),("net.minecraft.world.entity.LivingEntity","hurtServer")]:
    for k, v in fields_in(cls, pre).items():
        keep = sorted(set(x for x in v if not x.endswith(("level","random","entity","tickCount","lastSentXRot","lastSentYRot"))))
        lines.append(f"{cls.split('.')[-1]}.{k} fields: " + ", ".join(keep)[:800])
src = javap("net.minecraft.world.entity.Entity")
lines.append("Entity bool fields: " + ", ".join(sorted(set(re.findall(r"// Field (\w*(?:[Ss]ync|[Hh]urt|[Mm]arked)\w*):Z", src)))))
for i, l in enumerate(lines[:48]):
    lvl = "error" if i < 10 else ("warning" if i < 20 else "notice")
    print(f"::{lvl} title={tag}-{i}::{l[:900]}")
print("\n".join(lines))
