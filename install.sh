#!/bin/bash
# Picture Book Generator - 安装脚本
# 用于首次 checkout 代码后的环境准备和依赖安装

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 主安装流程
main() {
    print_header "Picture Book Generator 安装脚本"
    
    # 1. 检查 Python 版本
    print_info "检查 Python 环境..."
    if ! command_exists python3; then
        print_error "未找到 python3，请先安装 Python 3.10+"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "找到 Python $PYTHON_VERSION"
    
    # 检查 Python 版本是否 >= 3.10
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        print_error "Python 版本需要 >= 3.10，当前版本: $PYTHON_VERSION"
        exit 1
    fi
    
    # 2. 检查 pip
    if ! command_exists pip3; then
        print_error "未找到 pip3，请先安装 pip"
        exit 1
    fi
    print_success "找到 pip3"
    
    # 3. 创建虚拟环境（可选）
    echo ""
    read -p "是否创建虚拟环境? (推荐) [Y/n]: " create_venv
    create_venv=${create_venv:-Y}
    
    if [[ $create_venv =~ ^[Yy]$ ]]; then
        if [ -d "venv" ]; then
            print_warning "虚拟环境已存在"
        else
            print_info "创建虚拟环境..."
            python3 -m venv venv
            print_success "虚拟环境创建成功"
        fi
        
        print_info "激活虚拟环境..."
        source venv/bin/activate
        print_success "虚拟环境已激活"
    fi
    
    # 4. 安装核心依赖
    print_header "安装依赖"
    print_info "安装核心依赖..."
    pip install -e . -q
    print_success "核心依赖安装完成"
    
    # 5. 询问是否安装可选依赖
    echo ""
    read -p "是否安装 NotebookLM 集成依赖? [Y/n]: " install_notebooklm
    install_notebooklm=${install_notebooklm:-Y}
    
    if [[ $install_notebooklm =~ ^[Yy]$ ]]; then
        print_info "安装 NotebookLM 依赖..."
        pip install -e ".[notebooklm]" -q
        print_success "NotebookLM 依赖安装完成"
    fi
    
    echo ""
    read -p "是否安装开发依赖 (测试、linting)? [y/N]: " install_dev
    install_dev=${install_dev:-N}
    
    if [[ $install_dev =~ ^[Yy]$ ]]; then
        print_info "安装开发依赖..."
        pip install -e ".[dev]" -q
        print_success "开发依赖安装完成"
    fi
    
    # 6. 检查 .env 文件
    print_header "配置文件"
    if [ ! -f ".env" ]; then
        print_warning ".env 文件不存在"
        read -p "是否从 .env.example 创建 .env? [Y/n]: " create_env
        create_env=${create_env:-Y}
        
        if [[ $create_env =~ ^[Yy]$ ]]; then
            cp .env.example .env
            print_success ".env 文件已创建"
            print_warning "请编辑 .env 文件并填入你的 LLM API 配置"
        fi
    else
        print_success ".env 文件已存在"
    fi
    
    # 7. 创建输出目录
    if [ ! -d "output" ]; then
        mkdir -p output
        print_success "创建 output 目录"
    fi
    
    # 8. 验证安装
    print_header "验证安装"
    print_info "验证命令行工具..."
    if command_exists picture-book; then
        print_success "picture-book 命令可用"
        picture-book --version
    else
        print_error "picture-book 命令未找到"
        print_warning "如果使用虚拟环境，请确保已激活: source venv/bin/activate"
    fi
    
    # 9. 显示后续步骤
    print_header "安装完成！"
    echo ""
    print_success "环境准备完成！"
    echo ""
    echo "后续步骤："
    echo ""
    
    if [[ $create_venv =~ ^[Yy]$ ]]; then
        echo "1. 激活虚拟环境:"
        echo "   ${GREEN}source venv/bin/activate${NC}"
        echo ""
    fi
    
    echo "2. 配置 LLM API:"
    echo "   ${GREEN}编辑 .env 文件${NC}"
    echo "   填入你的 LLM_PROVIDER 和对应的 API_KEY"
    echo ""
    
    if [[ $install_notebooklm =~ ^[Yy]$ ]]; then
        echo "3. (可选) 登录 NotebookLM:"
        echo "   ${GREEN}notebooklm login${NC}"
        echo ""
    fi
    
    echo "4. 生成你的第一本绘本:"
    echo "   ${GREEN}picture-book generate dinosaur${NC}"
    echo ""
    
    if [[ $install_notebooklm =~ ^[Yy]$ ]]; then
        echo "5. 生成带 Slides 的绘本:"
        echo "   ${GREEN}picture-book generate ocean --nlm-slides${NC}"
        echo ""
    fi
    
    echo "更多信息请查看 README.md"
    echo ""
}

# 运行主函数
main
