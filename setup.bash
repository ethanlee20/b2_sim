function my_script_main()
{
    local original_dir="$PWD"
    cd /home/belle/sibid/belle2
    source tools/b2setup
    cd release
    b2setup
    cd $original_dir
}

my_script_main