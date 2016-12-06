# Ibex-in-toto demo

In this demo, we will use in-toto to secure a software supply chain and git with a very
simple workflow.
Alice will be the project owner - she creates and signs the software supply chain
layout with her private key - and Bob, Steve and Carl will be the project functionaries -
they carry out the steps of the software supply chain as defined in the layout.

For the sake of demonstrating Ibex-in-toto, we will have you run all parts of the
software supply chain.
This is, you will perform the commands on behalf of Alice, Bob, Steve and Carl as well
as the client who verifies the final product.


### Download and setup in-toto on *NIX (Linux, OS X, ..)
```shell
# Make sure you have git, python and pip installed on your system
# and get in-toto
git clone -b develop --recursive https://github.com/pkmoore/in-toto.git

# Change into project root directory
cd in-toto

# Install with pip in "develop mode"
# (we strongly recommend using Virtual Environments)
# http://docs.python-guide.org/en/latest/dev/virtualenvs/
sudo pip install -e .

# Export the envvar required for "simple settings"
export SIMPLE_SETTINGS=toto.settings

# Install additional requirements that for some good reason are not in the
# requirements file
sudo pip install pycrypto cryptography

# Change into the demo directoy and you are ready to start
cd demo
```
Inside the demo directory you will find four directories: `owner_alice`,
`functionary_bob`,`functionary_steve`, `functionary_carl` and `final_product`. Alice, Bob, Steve and Carl
already have RSA keys in each of their directories. This is what you see:
```shell
tree
# the tree command gives you the following output
#.
#├── final_product
#│   └── allowed_committers.json
#├── functionary_bob
#│   ├── bob
#│   ├── bob.pub
#│   └── foo.py
#├── functionary_carl
#│   ├── carl
#│   └── carl.pub
#├── functionary_steve
#│   ├── steve
#│   └── steve.pub
#├── git-securefetch
#├── git-securepush
#├── owner_alice
#│   ├── alice
#│   ├── alice.pub
#│   └── create_layout.py
#├── README.md

```
# Pre demo step
Before proceeding, check if remote branch 'bsl' is resent and delete it if present.
Then fetch using the given vcs script.
```shell
#delete bsl branch and fetch
git push origin --delete bsl
./git-securefetch
```

### Define software supply chain layout (Alice)
First, we will need to define the software supply chain layout. To simplify this
process, we provide a script that generates a simple layout for the purpose of
the demo. In this software supply chain layout, we have Alice, who is the project
owner that creates the layout, Bob, who uses `vi` to create a Python program
`foo.py`, Steve then uses `parsebsl.py` to create `bsl.json` as a pre packagng step and Carl, who uses `tar` to package up `foo.py` into a tarball which
together with the in-toto metadata composes the final product that will
eventually be installed and verified by the end user.

```shell
# Create and sign the software supply chain layout on behalf of Alice
cd owner_alice
python create_layout.py
```
The script will create a layout, add Bob's and Carl's public keys (fetched from
their directories), sign it with Alice's private key and dump it to `root.layout`.
In `root.layout`, you will find that (besides the signature and other information)
there are three steps, `write_code`, `post-vcs` and `package`, that the functionaries Bob,
Steve and Carl, identified by their public keys, are authorized to perform.

### Write code (Bob)
Now, we will take the role of the functionary Bob and perform the step
`write-code` on his behalf, that is we use in-toto to open an editor and record
metadata for what we do. Execute the following commands to change to Bob's
directory and perform the step.

```shell
cd ../functionary_bob
toto-run.py --step-name write-code --products foo.py --key bob -- vi foo.py
```

The command you just entered will open a `vi` editor, where you can write your
code (you can write whatever you want). After you save the file and close vi
(do this by entering `:x`), you will find `write-code.link` inside
Bob's directory. This is one piece of step link metadata that the client will
use for verification.

Here is what happens behind the scenes:
 1. In-toto wraps the command `vi foo.py`,
 1. hashes the product `foo.py`,
 1. stores the hash to a piece of link metadata,
 1. signs the metadata with Bob's private key and
 1. stores everything to `write-code.link`.

```shell
#Bob has to commit the changes and push the changes to git
git add foo.py
git commit -m "my commit "
cd ..
./git-securepush
cd functionary_bob
```

```shell
# Bob has to send the resulting foo.py to Carl so that he can package it
cp foo.py ../functionary_carl/
```

### Post-vcs (Steve)
Now, we will perform Steve’s `post-vcs` step.
Execute the following commands to change to Steve's directory and use `parsebsl.py` to create
`bsl.json`:

```shell
cd ../functionary_steve
toto-run.py --step-name after-vcs --products bsl.json --key steve -- parsebsl.py
```

This will create another step link metadata file, called `post-vcs.link`.

### Package (Carl)
Now, we will perform Carl’s `package` step.
Execute the following commands to change to Carl's directory and `tar` up Bob's
`foo.py`:

```shell
cd ../functionary_carl
toto-run.py --step-name package --materials foo.py --products foo.tar.gz --key carl -- tar zcvf foo.tar.gz foo.py
```

This will create another step link metadata file, called `package.link`.
It's time to release our software now.


### Verify final product (client)
Let's first copy all relevant files into the `final_product` that is
our software package `foo.tar.gz` and the related metadata files `root.layout`,
`write-code.link`, `post-vcs.link`, `bsl.json` and `package.link`:
```shell
cd ..
cp owner_alice/root.layout functionary_bob/write-code.link functionary_steve/after-vcs.link functionary_steve/bsl.json functionary_carl/package.link functionary_carl/foo.tar.gz final_product/
```
And now run verification on behalf of the client:
```shell
cd final_product
# Fetch Alice's public key from a trusted source to verify the layout signature
# Note: The functionary public keys are fetched from the layout
cp ../owner_alice/alice.pub .
toto-verify.py --layout root.layout --layout-key alice.pub
```
This command will verify that
 1. the layout has not expired,
 2. was signed with Alice’s private key,
<br>and that according to the definitions in the layout
 3. each step was performed and signed by the authorized functionary
 4. the functionaries used the commands they were supposed to use (`vi`,`parsebsl.py`
    `tar`)
 5. the recorded materials and products align with the matchrules and
 6. the inspection `untar` finds what it expects.


From it, you will see the meaningful output `PASSING` and a return value
of `0`, that indicates verification worked out well:
```shell
echo $?
# should output 0
```

