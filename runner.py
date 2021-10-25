#! /usr/bin/env python3

import yaml
import argparse
import sys
import subprocess
import time
import re

parser= argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="The yaml file to be opened")
parser.add_argument("-o", "--output", help="Output file")

args = parser.parse_args()
if not args.config:
    print("you need to specify a config file with -c")
    sys.exit()

if not args.output:
    args.output = "runner.log"

with open(args.config, "r") as yml:
    y = yaml.load(yml)
f = y['output']
v = list(dict(y["variables"]).keys())
c = y['command']
derived = list(dict(y["derived"]).keys())

def generate(y,c,f,v,s):
    if not len(v):
        p = ", ".join(s)
        return [(c,f,p)]
    cur = v[0]
    rest = v.copy()
    rest.pop(0)
    results = []
    for x in y["variables"][cur]:
        a = "{%s}" % (cur)
        b = str(x)
        d = c.replace(a, b)
        g = f.replace(a, b)
        t = s.copy()
        t.append(b)
        n = generate(y, d, g, rest, t)
        results = results + n
    return results

results = generate(y,c,f,v,[])
log = open(args.output, "w")
v.append("elapsed")
v = v + derived
log.write(", ".join(v)+"\n")

def getvalue(filename, matcher):
    last = None
    comp = re.compile(matcher)
    with open(filename, "r") as x:
        for line in x.readlines():
            m = comp.match(line)
            if m:
                last = m.group(1)
    return last

for r in results:
    cmd = r[0]
    out = r[1]
    pre = r[2]
    print(r)
    start = time.time()
    with open(out, "w") as x:
        p = subprocess.run(cmd, shell=True, stdout=x, stderr=x)
    end = time.time()
    elapsed=str(end-start)
    print("elapsed=",elapsed)

    values = [pre,elapsed]
    for e in derived:
        rx =y["derived"][e]
        x = getvalue(out, rx)
        print(f"{e}= {x}")
        values.append(x)

    txt = ", ".join(values)
    log.write(txt+"\n")
    log.flush()

