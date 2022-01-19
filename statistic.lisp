;(ql:quickload :cl-csv)
;(ql:quickload "parse-float")
;(use-package :parse-float)
;(load "statistic.lisp")

(defvar dataset (cl-csv:read-csv #P"stat.csv"))

(defun get-score-list (dataset)
  (let ((score-list ()))
    (dolist (el (cdr dataset))
      (setq score-list (append score-list
                               (list (parse-integer (nth 1 el)))
                               )))
    (return-from get-score-list score-list)
    )
  )


(defun get-time-list (dataset)
  (let ((time-list ()))
    (dolist (el (cdr dataset))
      (setq time-list (append time-list
                              (list (parse-float (nth 2 el)))
                              )))
    (return-from get-time-list time-list)
    )
  )


(defun get-expected-value (list-of-numbers)
  (let ((sum 0))
    (dolist (el list-of-numbers)
      (setq sum (+ sum el))
      )
    (return-from get-expected-value (/ sum (list-length list-of-numbers)))
    )
  )

(defun get-dispersion (list-of-numbers)
  (let (
        (list-in-square ())
        (mean  (get-expected-value list-of-numbers))
        )
    (dolist (el list-of-numbers)
      (setq list-in-square (append list-in-square (list (* el el))))
      )
    (return-from get-dispersion (- (get-expected-value list-in-square)
                                   (* mean mean))
      )
    )
  )


(terpri)
(format t "Expected value of time: ~a" (get-expected-value (get-time-list dataset)))
(terpri)
(format t "Dispersion of score: ~a" (get-dispersion (get-score-list dataset)))
(terpri)
