from text_util import check_answer_status


def test_check_answer_status():

    assert check_answer_status(["A long answer", "1"], "1") == "answered"
    assert check_answer_status(["A long answer", "1"], "2") == "fail", "Short answers allow no inaccuracy"
    assert check_answer_status(["A long answer", "1"], "A long answe") == "answered"
    assert check_answer_status(["A long answer", "1"], "A long answ") == "close_to_answer"
