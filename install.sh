# !/bin/zsh

WORKDIR="$HOME/.keypass_backup"

# install staff
brew install pyenv-virtualenv
brew install coreutils

# create venv
pyenv virtualenv 3.10.4 keypass-backup
pyenv shell keypass-backup
pip install -r requirements.txt
export PYENV_PYTHON=`which python`

# test
pytest || exit

# create WORKDIR
rm -rf "${WORKDIR}"
mkdir -p "${WORKDIR}"

# copy FILES
FILES="client_secrets.json config.yaml credentials.json settings.yaml"
for file in $FILES ; do
    if [ ! -f "${file}" ]; then
        cp "${file}.tmpl" "${file}"
    fi
    cp "${file}" "${WORKDIR}/"
done
for src in `ls ./src/*.py` ; do
    cp "${src}" "${WORKDIR}/"
done

export TIMEOUT_CMD=`which timeout`
envsubst '$PYENV_PYTHON,$TIMEOUT_CMD' < run.sh.tmpl > run.sh

cp ./run.sh ${WORKDIR}/
chmod +x ${WORKDIR}/run.sh

# setup daily launchd job
launchctl unload $HOME/Library/LaunchAgents/keypass.backup.daily.plist
envsubst < keypass.backup.daily.plist.tmpl > keypass.backup.daily.plist
cp keypass.backup.daily.plist $HOME/Library/LaunchAgents/
launchctl load $HOME/Library/LaunchAgents/keypass.backup.daily.plist
