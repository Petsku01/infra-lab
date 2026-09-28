#!/bin/bash
# Container entrypoint script
# Author: pk

set -e

export HOME=/home/user
export SHELL=/bin/zsh

# MOTD
[ -f /etc/motd ] && cat /etc/motd

# Setup dirs
mkdir -p /home/user/data /home/user/.ssh
chown -R user:user /home/user/data /home/user/.ssh
chmod 700 /home/user/.ssh
chmod 755 /home/user/data

# Validate SSH keys if present
if [ -f /home/user/.ssh/authorized_keys ]; then
  chmod 600 /home/user/.ssh/authorized_keys
  if ! ssh-keygen -l -f /home/user/.ssh/authorized_keys > /dev/null 2>&1; then
    logger "Warning: Invalid SSH key format in authorized_keys, removing file"
    rm -f /home/user/.ssh/authorized_keys
  fi
fi

# Start SSH if enabled
if [ "$ENABLE_SSH" = "true" ]; then
  /usr/sbin/sshd -D &
fi

# Start code-server if enabled
if [ "$ENABLE_CODE_SERVER" = "true" ]; then
  gosu user code-server --bind-addr 0.0.0.0:8080 --auth password --user-data-dir /home/user/data &
fi

# Run scripts (only if they exist and are in whitelist)
ALLOWED_SCRIPTS=("help.sh" "setup_user.sh" "example.sh")
SCRIPT_ERRORS=0
if [ -d /home/user/scripts ]; then
  for script in /home/user/scripts/*.sh; do
    script_name=$(basename "$script")
    if [[ " ${ALLOWED_SCRIPTS[@]} " =~ " ${script_name} " ]]; then
      if [ -x "$script" ]; then
        if ! gosu user "$script"; then
          logger "Error: $script failed with exit code $?"
          ((SCRIPT_ERRORS++))
        fi
      else
        logger "Warning: $script is not executable"
      fi
    else
      logger "Warning: $script not in whitelist, skipping"
    fi
  done
  
  # Exit if critical scripts failed (setup_user.sh is critical)
  if [ $SCRIPT_ERRORS -gt 0 ] && [[ " ${ALLOWED_SCRIPTS[@]} " =~ " setup_user.sh " ]]; then
    logger "Critical: Script failures detected, check logs"
    # Don't exit for non-critical failures, just log
  fi
fi

# Help handling
if [ "$1" = "help" ]; then
  gosu user /home/user/scripts/help.sh
  exit 0
fi

# Exec command or shell
if [ $# -gt 0 ]; then
  exec gosu user "$@"
else
  exec gosu user /bin/zsh
fi
