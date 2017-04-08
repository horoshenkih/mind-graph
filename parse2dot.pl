#!/usr/bin/perl
use strict;
use utf8;
use open ':utf8';
binmode STDIN, ':utf8';
binmode STDOUT, ':utf8';

use Data::Dumper;

my @COLORS = qw(blue green red);

# parse input
my %relations;  # relation => [[from1, to1], [from2,to2]]

while(<>) {
	chomp;
	# clean up text
	s/^\s+//;
	next unless $_;
	next if /^#/;  # comment
	s/\s+$//;
	s/\s+/ /;

	# some text @relation some other text
	/^(.+)\s+@(\S+)\s+(.+)/;
	push @{$relations{$2}}, [$1, $3];
}

#print Dumper \%relations;

# generate output
my @edges_repr;
my $i = 0;
my $n_relations = scalar keys %relations;
for my $relation (keys %relations) {
	my $color = $COLORS[$i++ % $n_relations];
	for my $edge (@{$relations{$relation}}) {
  	push @edges_repr, quote($edge->[0]) . " -> " . quote($edge->[1]) . " [color=$color]";
	}
}

printf "digraph G {\n%s\n}\n", join(";\n", map {"  $_"} @edges_repr);

sub quote {
	my $s = shift;
	return qq("$s");
}

1;
