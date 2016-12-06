### Use these scripts instead of git push and git fetch to maintain a BSL metadata branch. 

`git-securefetch` and `git-securepush` are bash scripts to be 
used by toto clients instead of normal `git fetch` and `git push`.
The scripts are responsible in maintaining a seperate branch of the 
repo called as `bsl` which has only one file also called `bsl`.

Whenever there is a fetch/push from/to the remote to local, 
the scripts use the local user's gpg authentication key to append
a signed entry of the repo metadata changes. This would log the metadata changes 
in a log and thus during client verification, if an unauthorized user had 
checked-in code or if the metadata were tampered at any point, 
it would not be in accordance with the bsl and throw an error.
