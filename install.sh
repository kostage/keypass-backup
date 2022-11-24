# !/bin/zsh

workdir="$HOME/.keypass_backup"

# install pyenv
brew install pyenv-virtualenv

# create venv
pyenv virtualenv 3.10.4 keypass-backup
pyenv shell keypass-backup
pip install -r requirements.txt

# test
pytest || exit

# create workdir
rm -rf "${workdir}"
mkdir -p "${workdir}"

# copy files
files="client_secrets.json config.yaml credentials.json settings.yaml"
for file in $files ; do
    if [ ! -f "${file}" ]; then
        cp "${file}.tmpl" "${file}"
    fi
    cp "${file}" "${workdir}/"
done
for src in `ls ./src/*.py` ; do
    cp "${src}" "${workdir}/"
done

export PYENV_PYTHON=`pyenv which python`
envsubst < run.sh.tmpl > run.sh

cp ./run.sh ${workdir}/
chmod +x ${workdir}/run.sh

# setup daily launchd job
launchctl unload $HOME/Library/LaunchAgents/keypass.backup.daily.plist
envsubst < keypass.backup.daily.plist.tmpl > keypass.backup.daily.plist
cp keypass.backup.daily.plist $HOME/Library/LaunchAgents/
launchctl load $HOME/Library/LaunchAgents/keypass.backup.daily.plist
