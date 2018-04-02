
# ReNomDP

ReNom DP is data preprocess tool.

## Install
ReNomDP requires ReNom.

If you haven't install ReNom, you must install ReNom from www.renom.jp.

For installing ReNomDP, download the repository from following url.

`git clone https://gitlab.com/grid-devs/ReNomDP.git`

And move into ReNomDP directory.
`cd ReNomDP`

Then install all required packages.

`pip install -r requirements.txt`


## How to start

1.Move to ReNomDP directory using following command.

`cd ReNomDP`

2. Create data directory, and put your csv file to here.

`mkdir data`

`cp <csvfile path> <ReNom DP installed path>/ReNomDP/data/`

3.Run server.py script and the application server starts.

`python server.py`

And you wan't to change default port, you can use --port arguments.

`python server.py --port=12345`


## License

“ReNomDP” is provided by GRID inc., as subscribed software.  By downloading ReNomDP, you are agreeing to be bound by our ReNom Subscription agreement between you and GRID inc.
To use ReNomDP for commercial purposes, you must first obtain a paid license. Please contact us or one of our resellers.  If you are an individual wishing to use ReNomDP for academic, educational and/or product evaluation purposes, you may use ReNomDP royalty-free.
The ReNom Subscription agreements are subject to change without notice. You agree to be bound by any such revisions. You are responsible for visiting www.renom.jp to determine the latest terms to which you are bound.
