#
ffmpeg -framerate 1/10 -i *%04d.png -c:v libx264 -r 30 -pix_fmt yuv420p graph.mp4

cat *.png | ffmpeg -f image2pipe -i pipe:.png -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p output.mp4


cat *.png | ffmpeg -f image2pipe -i pipe:.png -c:v libx264 -r 30 -pix_fmt yuv420p graph.mp4 

cat *.png | ffmpeg -f image2pipe -i pipe:.png -c:v mpeg2video -r 20 -pix_fmt yuv420p flood-7d.mp4 


ffmpeg -codecs
ffmpeg -formats

