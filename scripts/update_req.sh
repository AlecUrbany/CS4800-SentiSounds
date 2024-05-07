# Usage: update_req.sh requirements.txt
REPO=~/CS4800-SentiSounds
$REPO/venv/bin/pip install --upgrade -r $1
while read line; do
    package=$(echo "$line" | cut -d'=' -f1)
    version=$(pip freeze | grep "^$package==" | cut -d'=' -f3)
    if [ -n "$version" ]; then
        sed -i "s/^$package=.*/$package==$version/" $1
    fi
done < $1
