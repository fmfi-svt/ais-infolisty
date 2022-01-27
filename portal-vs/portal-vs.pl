#! /usr/bin/perl -w
use strict;
use utf8;

my $url = "https://www.portalvs.sk/regzam/?do=filterForm-submit&university=701000000&sort=surname&employment_state=yes";

`wget -O temp.txt --keep-session-cookies --save-cookies cookies.txt`;

my $meno = "";
my $linka = "";
my $fakulta = "";
binmode STDOUT,":utf8";

for (my $i=1; $i<63; $i++) {
    unlink("temp.txt");
    `wget -O temp.txt --load-cookies cookies.txt '$url&vp-page=$i'`;
    open IN,"<:encoding(UTF-8)","temp.txt";
    
    while (my $line=<IN>) {
	if ($line =~ /\<a href=\"(\/regzam\/detail\/.*)\?do=.*>(.*)<\/a>/) {
	    if ($meno) {
		print join("\t",$meno,$linka,$fakulta),"\n";
	    }
	    $meno = lc($2);
	    $linka = $1;
	    $fakulta = "";
	}

	if ($line =~ /center.*>(.*)<\/abbr>/) {
	    $fakulta = $1;
	}
    }
}

if ($meno) {
    print join("\t",$meno,$linka,$fakulta),"\n";
}
