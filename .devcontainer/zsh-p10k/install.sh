#!/usr/bin/env bash

set -e

REMOTE_USER_HOME="/home/${_REMOTE_USER}"
ZSH_CUSTOM="${REMOTE_USER_HOME}/.oh-my-zsh/custom"

echo "🔧 Installing Powerlevel10k theme..."

# Clone the Powerlevel10k repo
if [ ! -d "${ZSH_CUSTOM}/themes/powerlevel10k" ]; then
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "${ZSH_CUSTOM}/themes/powerlevel10k"
else
    echo "⚠️ Powerlevel10k already installed."
fi

# Update .zshrc to source Powerlevel10k
ZSHRC="${REMOTE_USER_HOME}/.zshrc"

# Only append if not already present
if ! grep -q "powerlevel10k/powerlevel10k" $ZSHRC; then
    sed -i 's/^ZSH_THEME=.*/ZSH_THEME="powerlevel10k\/powerlevel10k"/' $ZSHRC

    echo "✅ Added Powerlevel10k to .zshrc"
else
    echo "✅ Powerlevel10k already configured in .zshrc"
fi

echo "✅ Installation complete."
