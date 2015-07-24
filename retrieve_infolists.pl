#! /usr/bin/perl -w
use strict;
use File::Temp qw/ tempfile tempdir /;
use FindBin qw($Bin);

my $usage = "
$0 season target_directory
";

my $season = shift or die $usage;
my $fakulta = "FMFI";
my $target_directory = shift or die $usage;
my $xmlurl = "https://ais2.uniba.sk/repo2/repository/default/ais/informacnelisty";

my $tempdir = tempdir( CLEANUP=>1 );

download_data("sk");
download_data("en");
process_data("sk","regular","template_table_sk.html");
process_data("en","regular","template_table_en.html");
process_data("sk","statnice","template_statne-skusky_table_sk.html");
process_data("en","statnice","template_statne-skusky_table_en.html");




sub process_data {
    my ($lang,$mode,$sablona) = @_;
    
    my $ultimatetarget = "$target_directory/$season/$lang";
    print STDERR "Processing $lang/$mode into $ultimatetarget...\n";

    my_run("mkdir -p $ultimatetarget");
    my_run("python $Bin/AIS_XML2HTML.py --lang $lang --mode $mode $tempdir/$fakulta/xml_files_$lang $ultimatetarget templates/$sablona");
}


sub download_data {
    my ($lang) = @_;

    print STDERR "Retrieving data for language $lang...\n";

    my $LANG = uc $lang;
    my $datadir="$tempdir/$fakulta";
    my $filelist="$datadir/files_$lang.txt";
    my $xmldir="$datadir/xml_files_$lang";

    my $lynxcmd = "lynx --dump \"$xmlurl/$season/$fakulta/$LANG/\" | awk '/http/{print \$2}' | grep xml > \"$filelist\"";
    my $wgetcmd = "wget -N -q -i \"$filelist\" -P \"$xmldir\"";


    my_run("mkdir -p $datadir");
    my_run("mkdir -p $xmldir");
    my_run($lynxcmd);
    my_run($wgetcmd);
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
