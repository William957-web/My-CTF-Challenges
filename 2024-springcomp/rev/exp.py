import angr

proj = angr.Project('./test')

simgr = proj.factory.simgr()

simgr.explore(find=lambda s: (b"flydrago" in s.posix.dumps(1)))

print(simgr.found[0].posix.dumps(0))
