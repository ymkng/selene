"""
TODO
"""
from scipy.special import logit

from .handler import _create_warning_handler
from .handler import PredictionsHandler
from .handler import write_to_file


class LogitScoreHandler(PredictionsHandler):
    """
    The logit score handler calculates and records the
    difference between `logit(alt)` and `logit(ref)` predictions.
    For reference, if some event occurs with probability :math:`p`,
    then the log-odds is the logit of `p`, or

    .. math::
        \\mathrm{logit}(p) = \\log\\left(\\frac{p}{1 - p}\\right) =
        \\log(p) - \\log(1 - p)

    Parameters
    ----------
    features : list of str
        List of sequence-level features, in the same order that the
        model will return its predictions.
    nonfeature_columns : list of str
        Columns in the file that help to identify the input sequence to
        which the features data corresponds.
    output_path : str
        Path to the file where the logit scores will be written.

    Notes
    -----



    """

    def __init__(self,
                 features,
                 nonfeature_columns,
                 output_path):
        """
        Constructs a new `LogitScoreHandler` object.
        """
        super(LogitScoreHandler).__init__()

        self.needs_base_pred = True
        self._results = []
        self._samples = []
        self._NA_samples = []

        self._features = features
        self._nonfeature_columns = nonfeature_columns
        self._output_path = output_path

        self._output_handle = open(self._output_path, 'w+')
        column_names = nonfeature_columns + features
        self._output_handle.write("{0}\n".format(
            '\t'.join(column_names)))

        self._warn_handler = None

    def handle_NA(self, batch_ids):
        """
        TODO

        Parameters
        ----------
        batch_ids : # TODO
            # TODO

        """
        super().handle_NA(batch_ids)

    def handle_warning(self,
                       batch_predictions,
                       batch_ids,
                       baseline_predictions):
        if self._warn_handler is None:
            self._warn_handler = _create_warning_handler(
                self._features,
                self._nonfeature_columns,
                self._output_path,
                LogitScoreHandler)
        self._warn_handler.handle_batch_predictions(
            batch_predictions, batch_ids, baseline_predictions)

    def handle_batch_predictions(self,
                                 batch_predictions,
                                 batch_ids,
                                 baseline_predictions):
        """
        # TODO

        Parameters
        ----------
        batch_predictions : arraylike
            The predictions for a batch of sequences. This should have
            dimensions of :math:`B \\times N` (where :math:`B` is the
            size of the mini-batch and :math:`N` is the number of
            features).
        batch_ids : list(arraylike)
            Batch of sequence identifiers. Each element is `arraylike`
            because it may contain more than one column (written to
            file) that together make up a unique identifier for a
            sequence.
        base_predictions : arraylike
            The baseline prediction(s) used to compute the logit scores.
            This must either be a vector of :math:`N` values, or a
            matrix of shape :math:`B \\times N` (where :math:`B` is
            the size of the mini-batch, and :math:`N` is the number of
            features).

        """
        logits = logit(baseline_predictions) - logit(batch_predictions)
        self._results.append(logits)
        self._samples.append(batch_ids)
        if len(self._results) > 100000:
            self.write_to_file()

    def write_to_file(self, close=False):
        """
        TODO
        """
        if not self._results:
            self._output_handle.close()
            return None
        write_to_file(self._results,
                      self._samples,
                      self._output_handle,
                      close=close)
        self._results = []
        self._samples = []
