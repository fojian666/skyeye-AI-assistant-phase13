#!/usr/bin/env bash
#
# SkyEye Git Push 脚本
# 用法:
#   ./push.sh                        # 使用默认 commit message
#   ./push.sh "feat: 你的提交信息"    # 自定义 commit message
#   ./push.sh -m "fix: bug修复"      # -m 方式指定 message
#
# 推送目标:
#   1. phase12  — GitHub 独立 Phase 仓库 (新建/复用)
#   2. gitee    — Gitee 主仓库
#   3. skyeye-ui-gitee — Gitee 前端仓库

set -euo pipefail

# ============================================================
# 远程仓库配置（按需修改）
# ============================================================
PHASE_REMOTE="phase12"
PHASE_URL="https://github.com/fojian666/skyeye-AI-assistant-phase12.git"
GITEE_REMOTE="gitee"
GITEE_URL="https://gitee.com/njuptGIS/skyeye.git"
UI_GITEE_REMOTE="skyeye-ui-gitee"
UI_GITEE_URL="https://gitee.com/njuptGIS/skyeye-ui.git"

# 当前分支
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# 默认 commit message（Phase 12）
DEFAULT_MSG="feat: Phase 12 — 灵动岛一体化 + 手机外壳 + 四角缩放 + 会话抽屉无缝融合 + 点击外部收起"

# ============================================================
# 解析参数
# ============================================================
COMMIT_MSG="$DEFAULT_MSG"

if [[ $# -ge 2 && "$1" == "-m" ]]; then
    COMMIT_MSG="$2"
elif [[ $# -ge 1 && "$1" != "-m" ]]; then
    COMMIT_MSG="$1"
fi

echo "========================================"
echo " SkyEye Git Push"
echo "========================================"
echo " 分支:     $BRANCH"
echo " 提交信息: $COMMIT_MSG"
echo ""

# ============================================================
# 1. 确保 phase12 remote 存在
# ============================================================
setup_remote() {
    local name="$1"
    local url="$2"
    if git remote get-url "$name" &>/dev/null; then
        echo "✓ 远程 $name 已存在: $(git remote get-url "$name")"
    else
        echo "→ 添加远程 $name → $url"
        git remote add "$name" "$url"
        echo "✓ 已添加远程 $name"
    fi
}

setup_remote "$PHASE_REMOTE" "$PHASE_URL"
setup_remote "$GITEE_REMOTE" "$GITEE_URL"
setup_remote "$UI_GITEE_REMOTE" "$UI_GITEE_URL"
echo ""

# ============================================================
# 2. 检查是否有变更
# ============================================================
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo "⚠ 工作区无变更，跳过提交，仅 push。"
    SKIP_COMMIT=true
else
    SKIP_COMMIT=false
fi

# ============================================================
# 3. 提交
# ============================================================
if [ "$SKIP_COMMIT" = false ]; then
    echo "→ git add -A"
    git add -A
    echo "→ git commit"
    git commit -m "$COMMIT_MSG"
    echo "✓ 提交完成"
else
    echo "→ 跳过提交（无变更）"
fi
echo ""

# ============================================================
# 4. 推送到三个远程
# ============================================================
push_remote() {
    local name="$1"
    local target_branch="$2"
    echo "→ 推送 $name ($target_branch)..."
    if git push "$name" "$BRANCH:$target_branch" 2>&1; then
        echo "✓ $name 推送成功"
    else
        echo "✗ $name 推送失败，尝试 force-with-lease 或检查权限"
        return 1
    fi
}

# Phase12 推送到 main
push_remote "$PHASE_REMOTE" "main" || echo "⚠ 可稍后手动: git push $PHASE_REMOTE $BRANCH:main"

# Gitee 主仓库推送到 main
push_remote "$GITEE_REMOTE" "main" || echo "⚠ 可稍后手动: git push $GITEE_REMOTE $BRANCH:main"

# Gitee 前端仓库推送到 wuxi-ai
push_remote "$UI_GITEE_REMOTE" "wuxi-ai" || echo "⚠ 可稍后手动: git push $UI_GITEE_REMOTE $BRANCH:wuxi-ai"

echo ""
echo "========================================"
echo " 完成"
echo "========================================"
