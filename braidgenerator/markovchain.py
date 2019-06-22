import random
import copy
import pandas as pd
import functools
from copy import copy, deepcopy
from braidgenerator.braidword import BraidWord
from braidgenerator.decorators.markovchain import checkparams_markovchain


class MarkovChain:
    r"""MarkovChain is an encapsulation of the Markov Chain.
    It takes a BraidWord and allows modelling, which creates
    a specified number of braidreps along with the logs pertaining
    to that braidrep (i.e. which Markov Move was made at some iteration).

    Parameters
	----------
        braidword : :obj:`BraidWord`
            A BraidWord to have braidreps generated
            from it. Note that a simple Python list can be given as a
            parameter as well, which will be converted to a BraidWord behind
            the scenes.

        maxgen : :obj:`int`
            The maximum absolute value a generator can be in the
            BraidWord and its subsequent braidreps.

        maxlen : :obj:`int`
            The maxmimum length of that any subsequent braidreps
            can reach.

    Attributes
	----------
        braidagg : :obj:`dictionary`
            Dictionary that holds braidreps and logs.

	Examples
    --------
		>>> mc = MarkovChain(braidword=[1, 2, 3], maxgen=9, maxlen=10)
        >>> mc.braid.word
		[1, 2, 3]

		>>> mc.maxgen
		9

		>>> mc.maxlen
		10

    """
    @checkparams_markovchain
    def __init__(self, braidword: BraidWord,
                 maxgen: int = 9, maxlen: int = 10):
        # braidword
        self.braid = braidword
        # max generators
        self.maxgen = maxgen
        # max length of braidword
        self.maxlen = maxlen
        # braid aggregate
        self.braidagg = {
            # list of braidreps
            'braidreps': [],
            # list of logs
            'logs': []  # holds dict
        }

    @staticmethod
    def log_message(movetype: int, name: str, result: bool) -> str:
        r"""
        Function to dynamically create log of Markov Move @[mstep]

        Parameters
    	----------
            movetype : :obj:`int`
                Markov Move[i] for i in [0, 6], inclusive. There
                are 7 Markov Moves that determine the braid-to-braidrep
                modification.

            name : :obj:`str`
                The name of the Markov Move.

            result : :obj:`bool`
                Boolean representing whether the move was successfully
                executed or not.

        Returns
		-------
            String of log for BraidWord.word at Markov Move [i] for
            i in [0, 6], inclusive.

        """
        beg = f"MoveType: {str(movetype)}, "
        tmp = f"Attempted {name}: "
        if result == True:
            tmp += name + " Succeeded."
        else:
            tmp += name + " Failed."

        return beg + tmp

    def model(self, num_braidreps: int = 1, msteps: int = 100):
        r"""
        Method to model the BraidWord and generate braidreps and logs.
        A random number is picked between (0, 6), inclusive, determining the
        Markov Move to perform. Another random number is picked from
        range(len(BraidWord.word)) that represents the index of BraidWord.word
        to perform the Markov Move on. The braidrep is generated by picking a
        random index from the set of possible indices for BraidWord.word and a
        random Markov Move that acts on BraidWord.word at the given index.

        Parameters
		----------
            num_braidreps : :obj:`int`
                Number of braidreps to be modeled from
                the BraidWord given to the Markov Chain.

            msteps : :obj:`int`
                The number of steps to be taken until an braidrep
                is considered to be complete. That is, msteps many iterations
                of the model process take place on a given BraidWord.

        Returns
		-------
            Appends braidrep and log to self.braidagg.

        """
        # msteps: number of markov steps per iteration
        # num_braidreps: number of braidreps (iterations) to create
        rr = random.randrange  # Consider resetting seed
        for _ in range(num_braidreps):
            braid = self.braid  # Not copied purposefully
            log = {}
            # Perform markov moves on braid
            for step in range(msteps):
                movetype = rr(7)
                index = rr(braid.length())
                if movetype == 0:
                    if braid.conjugate(index):
                        # append logs success
                        log[step] = self.log_message(movetype, braid.conjugate.__name__, True)
                    else:
                        # append logs fail
                        log[step] = self.log_message(movetype, braid.conjugate.__name__, False)

                elif movetype == 1:
                    # Do not cancel if braid length is 2: unknot
                    if braid.length() == 2 and braid.canCancel(index):
                        log[step] = self.log_message(movetype, (braid.cancel).__name__, False)
                        log[step] += 'Unknot'
                        continue
                    elif braid.cancel(index):
                        # append logs success
                        log[step] = self.log_message(movetype, (braid.cancel).__name__, True)
                    else:
                        # append logs fail
                        log[step] = self.log_message(movetype, (braid.cancel).__name__, False)

                elif movetype == 2:
                    if (braid.length() <= self.maxlen-2
                        and braid.insert(index, rr(braid.largestGenerator + 1))):
                        # append logs success
                        log[step] = self.log_message(movetype, (braid.insert).__name__, True)
                    else:
                        # append logs fail
                        log[step] = self.log_message(movetype, (braid.insert).__name__, False)

                elif movetype == 3:
                    if braid.transpose(index):
                        # append logs success
                        log[step] = self.log_message(movetype, (braid.transpose).__name__, True)
                    else:
                        # append logs fail
                        log[step] = self.log_message(movetype, (braid.transpose).__name__, False)

                elif movetype == 4:
                    if braid.flip(index):
                        # append logs success
                        log[step] = self.log_message(movetype, (braid.flip).__name__, True)
                    else:
                        # append logs fail
                        log[step] = self.log_message(movetype, (braid.flip).__name__, False)

                elif movetype == 5:
                    if (braid.length() <= self.maxlen-1
                        and braid.largestGenerator < self.maxgen
                        and braid.stabilize()):
                        # append logs success
                        log[step] = self.log_message(movetype, (braid.stabilize).__name__, True)
                    else:
                        # append logs fail
                        log[step] = self.log_message(movetype, (braid.stabilize).__name__, False)

                elif movetype == 6:
                    # Do not destabilize if braid length is 1: unknot
                    if braid.length() == 1 and braid.canDestabilize():
                        log[step] = self.log_message(movetype, (braid.destabilize).__name__, False)
                        log[step] += 'Unknot'
                        continue
                    elif braid.destabilize():
                        # append logs success
                        log[step] = self.log_message(movetype, (braid.destabilize).__name__, True)
                    else:
                        # append logs fail
                        log[step] = self.log_message(movetype, (braid.destabilize).__name__, False)
                else:
                    # should not get to this point
                    continue

            # Append new braidrep and log
            self.braidagg['braidreps'] += [deepcopy(braid)]
            self.braidagg['logs'].append(log)

        return

    def clear_model(self):
        r"""
        Method to clear braid instance. That is, it clears `braidagg`.

        """
        self.braidagg = {
            # list of braidreps
            'braidreps': [],
            # list of logs
            'logs': []  # holds dict
        }

    def new_braidword(braidword: BraidWord):
        r"""
        Method to set a new BraidWord.

        Parameters
		----------
            braidword : :obj:`BraidWord`
                The new BraidWord to replace the old
                BraidWord.

        Returns
		-------
            Replaces self.braid with braidword.

        """
        # Check if is braidword
        if not isinstance(braidword, BraidWord):
            # Check if is list
            if not isinstance(braidword, list):
                msg = 'First argument must be BraidWord or list.'
                raise ValueError(msg)
            else:
                self.braid = BraidWord(deepcopy(braidword))

        else:
            self.braid = deepcopy(braidword)

    def aggregate(self):
        r"""
        Method to return a dictionary of MarkovChain instance's
        braidreps and logs, both contained in their respective lists.
        That is, returns self.braidagg.

        """
        return deepcopy(self.braidagg)

    def logs(self):
        r"""
        Method to return MarkovChain instance logs in a list.
        Note that the length of the list is equal to the number of
        braidreps requested in the num_braidreps argument of model.
        Each log represents the logs undergone to create a specific
        braidrep and is held in a dictionary. The size of the
        dictionary is equal to the argument passed for msteps in model.

        """
        return deepcopy(self.braidagg['logs'])

    def braidreps(self, as_word=False):
        r"""
        Method to return MarkovChain instance braidreps in a list.

        Parameters
		----------
            as_word : :obj:`bool`
                Determines if braidreps should be returned
                as words or BraidWords.

        Returns
		-------
            If True returns braidreps as words (list).
            Otherwise returns them as BraidWords (of class BraidWord).

        """
        isos = (self.braidagg['braidreps']).copy()
        if as_word:
            # Return list of words
            isos = [i.word for i in isos]
            return isos

        elif not as_word:
            # Return list of BraidWords
            return isos

        else:
            raise ValueError("as_word argument must be boolean.")
            return

    def topandas(self, only_braidreps=False):
        r"""
        Method to export logs, braidreps to pandas df.

        Parameters
		----------
            only_braidreps : :obj:`bool`
                Determines if only braidreps
                should be returned or both braidreps and logs.

        Returns
		-------
            If only_braidreps=True returns a pandas dataframe of
            only braidreps. Otherwise will return a pandas dataframe
            with both braidreps and logs.

        """
        isos = self.braidreps(as_word=True)
        logs = self.logs()
        dat = ({'braidreps': isos} if only_braidreps
               else {'braidreps': isos, "Logs": logs})
        df = pd.DataFrame(dat, index=[i for i in range(len(isos))])

        return df.copy()

    def tocsv(self, path_or_filename="", only_braidreps=False):
        r"""
        Method to export logs, braidreps to csv.
        If path_or_filename not given, will export the csv to
        current directory with the name `braidreps.csv` or
        `braidreps_and_Logs.csv`. The name is implicitly determined
        by the parameter passed to only_braidreps.

        Parameters
		----------
            path_or_filename : :obj:`str`
                Path or filename to store csv.

            only_braidreps : :obj:`bool`
                Determines if only braidreps should be returned or
                both braidreps and logs.

        Returns
		-------
            A csv file containing a dataframe with either only
            braidreps or both braidreps and logs, depending on parameter
            passed to only_braidreps.

        """
        # Set path_or_filename if not given
        if not path_or_filename:
            path_or_filename = ("braidreps.csv" if only_braidreps
                                else "braidreps_and_Logs.csv")
        # Get pandas df
        df = self.topandas(only_braidreps)
        # Export df to csv file on current directory
        df.to_csv(path_or_filename, sep='\t')

        return

    def totxt(self, path_or_filename="", only_braidreps=False):
        r"""
        Method to export logs, braidreps to a txt file.
        If path_or_filename not given, will export the csv to
        current directory with the name `braidreps.txt` or
        `braidreps_and_Logs.txt`. The name is implicitly determined
        by the parameter passed to only_braidreps.

        Note
        ----
            The format in the .txt is vertical, as follows:

            braidrep[1]

            ...

            braidrep[n]

            (`newline`)

            log[1]

            ...

            log[n]

        Parameters
		----------
            path_or_filename : :obj:`str`
                Path or filename to store txt.
            only_braidreps : :obj:`bool`
                Determines if only braidreps should be returned
                or both braidreps and logs.

        Returns
		-------
            A txt file containing a either only braidreps or both braidreps
            and logs, depending on parameter passed to only_braidreps.

        """

        # Set path_or_filename if not given
        if not path_or_filename:
            path_or_filename = ("braidreps.txt" if only_braidreps
                                else "braidreps_and_Logs.txt")

        # Write to txt
        with open(path_or_filename, 'w') as file:
            for braid in self.braidreps(as_word=True):
                file.write(' '.join(str(gen) for gen in braid))
                file.write('\n')
            file.write('\n')
        if not only_braidreps:
            with open(path_or_filename, 'a') as file:
                for log in self.logs():
                    file.write(str(log))
                    file.write('\n')
                file.write('\n')

        return