#!/bin/bash
# Run in the cloud (Java 21 + freerouting-2.1.0.jar + Route.class beside this script). Needs <tag>_pads.json (pads from the DSN).
# loop.sh base.dsn tag rounds passes : route, merge best result back, route again ...
B=$1; T=$2; R=${3:-4}; P=${4:-30}
cp $B ${T}_0.dsn
for r in $(seq 1 $R); do
  timeout 1200 java -cp $(dirname "$0")/freerouting-2.1.0.jar:$(dirname "$0") Route ${T}_$((r-1)).dsn ${T}_$r.ses $P > ${T}_$r.log 2>&1
  python3 $(dirname "$0")/check_ses.py ${T}_$r.ses ${T}_pads.json 2>&1 | tail -1 > ${T}_$r.chk
  echo "round $r: $(grep '^pass' ${T}_$r.log | sort -t' ' -k4 -n | head -1) | $(cat ${T}_$r.chk)" >> ${T}.progress
  grep -q " 0 net" ${T}_$r.chk && break
  grep -q "all nets" ${T}_$r.chk && break
  python3 $(dirname "$0")/merge.py ${T}_0.dsn ${T}_$r.ses ${T}_$r.dsn > /dev/null
done
echo done >> ${T}.progress
