#! /usr/bin/perl -w
use strict;
use File::Temp qw/ tempfile tempdir /;
use File::Basename;
use FindBin qw($Bin);
use Getopt::Std;

my $usage = "
$0 [-f faculty] season target_directory
";

my %opts;
getopts('f:',\%opts);

my $season = shift or die $usage;
my $fakulta = "FMFI";
my $fakulta = $opts{'f'} if defined $opts{'f'};
my $target_directory = shift or die $usage;
my $xmlurl = "https://ais2.uniba.sk/repo2/repository/default/ais/informacnelisty";

my $tempdir = tempdir( CLEANUP=>1 );

download_data("sk");
download_data("en");
process_data("sk","regular","template_2022_sk.html");
process_data("en","regular","template_2022_en.html");
process_data("sk","statnice","template_2022_sk.html");
process_data("en","statnice","template_2022_en.html");
create_links("sk");
create_links("en");


sub create_links {
    my ($lang) = @_;

    my $ultimatetarget = "$target_directory/$season/$lang";
    # make links
    my @allfiles = sort(glob("$ultimatetarget/*.html"));
    foreach my $file (@allfiles) {
	my $newfile = $file;
	my $oldfile = fileparse($file);
	$newfile =~ s/_\d+\.html/\.html/g;
	next if $newfile eq $file;
	my_run("ln -fs $oldfile $newfile");
    }
}

sub process_data {
    my ($lang,$mode,$sablona) = @_;
    
    my $ultimatetarget = "$target_directory/$season/$lang";
    print STDERR "Processing $lang/$mode into $ultimatetarget...\n";

    my_run("mkdir -p $ultimatetarget");
    my_run("python $Bin/AIS_XML2HTML.py --lang $lang --mode $mode --year $season $tempdir/$fakulta/xml_files_$lang $ultimatetarget templates/$sablona");

}


sub download_data {
    my ($lang) = @_;

    print STDERR "Retrieving data for language $lang...\n";

    my $LANG = uc $lang;
    my $datadir="$tempdir/$fakulta";
    my $filelist="$datadir/files_$lang.txt";
    my $xmldir="$datadir/xml_files_$lang";

    my $lynxcmd = "lynx --dump \"$xmlurl/$season/$fakulta/$LANG/\" | awk '/http/{print \$2}' | grep xml > \"$filelist\"";


    my_run("mkdir -p $datadir");
    my_run("mkdir -p $xmldir");
    my_run($lynxcmd);

    open IN,"<$filelist";
    while (my $file = <IN>) {
	## download file by file because wget has memory leak
	chomp $file;
	my $wgetcmd = "wget -N -q \"$file\" -P \"$xmldir\"";
	my_run($wgetcmd);
    }
    close IN;
}

sub my_run
{
    my ($run, $die) = @_;
    if(!defined($die)) { $die = 1; }

    my $short = substr($run, 0, 20);

    print STDERR $run, "\n";
    my $res = system($run);
    if($res<0) {
        die "Error in program '$short...' '$!'";
    }
    if($? && $die) {
        my $exit  = $? >> 8;
        my $signal  = $? & 127;
        my $core = $? & 128;

        die "Error in program '$short...' "
            . "(exit: $exit, signal: $signal, dumped: $core)\n\n ";
    }
}
