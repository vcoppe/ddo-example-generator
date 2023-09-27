cd out
find *.tex | xargs -n1 -P0 -I {} sh -c './compile.sh {}' sh {}