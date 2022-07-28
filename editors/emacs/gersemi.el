;;; gersemi.el --- Reformat CMake code using gersemi

;; Keywords: tools, cmake

;;; Commentary:
;; This module is part of gersemi: https://github.com/BlankSpruce/gersemi
;; which provides:
;; `gersemi-region` - reformats region with gersemi
;; `gersemi-buffer` - reformats selected buffer
;; `gersemi-mode` - minor mode which automatically reformats buffer before saving
;;
;; Consider adding hook:
;;
;; (add-hook 'cmake-mode-hook 'gersemi-mode)

;;; Code:
(defgroup gersemi nil
  "Format CMake code using gersemi"
  :group 'tools
  )

(defcustom gersemi-executable
  (or (executable-find "gersemi")
      "gersemi"
      )
  "Name or path to executable."
  :group 'gersemi
  :type '(file :must-match t)
  :risky t
  )

(defcustom gersemi-args '()
  "Arguments to be passed to executable."
  :group 'gersemi
  :type '(repeat string)
  :risky t
  )

(defun gersemi--make-args ()
  "Make proper list of arguments passed to gersemi."
  (append gersemi-args '("--" "-"))
  )

(defun gersemi--make-process (output-buffer error-buffer)
  "Make gersemi process.
Stdout and stderr are redirected to OUTPUT-BUFFER and ERROR-BUFFER respectively."
  (make-process
   :name "gersemi"
   :buffer output-buffer
   :command `(,gersemi-executable ,@(gersemi--make-args))
   :noquery t
   :sentinel (lambda (process event))
   :stderr error-buffer
   )
  )

(defun gersemi--invoke (input-buffer output-buffer error-buffer)
  "Invoke gersemi.
INPUT-BUFFER, OUTPUT-BUFFER and ERROR-BUFFER serve as stdin, stdout and stderr respectively."
  (with-current-buffer input-buffer
    (let ((process (gersemi--make-process output-buffer error-buffer)))
      (set-process-query-on-exit-flag (get-buffer-process output-buffer) nil)
      (set-process-query-on-exit-flag (get-buffer-process error-buffer) nil)
      (set-process-sentinel (get-buffer-process error-buffer) (lambda (process event)))
      (save-restriction
        (widen)
        (process-send-region process (point-min) (point-max))
        )
      (process-send-eof process)
      (accept-process-output process nil nil t)
      (while (process-live-p process)
        (accept-process-output process nil nil t)
        )
      (process-exit-status process)
      )
    )
  )

(defun gersemi--cleanup-buffer (buffer)
  (with-current-buffer buffer
    (erase-buffer)
    )
  )

(defun gersemi--cleanup-buffers (input-buffer output-buffer error-buffer)
  (mapc 'gersemi--cleanup-buffer (list input-buffer output-buffer error-buffer))
  )

(defun gersemi--replace (target-buffer start end source-buffer)
  "Replace region between START and END in TARGET-BUFFER with content of SOURCE-BUFFER."
  (with-current-buffer target-buffer
    (goto-char start)
    (delete-region start end)
    (insert-buffer-substring source-buffer)
    )
  )

(defun gersemi--prepare-buffers (original-buffer start end input-buffer output-buffer error-buffer)
  (gersemi--cleanup-buffers input-buffer output-buffer error-buffer)
  (with-current-buffer original-buffer
    (copy-to-buffer input-buffer start end)
    )
  )

(defun gersemi--restore-position (position-in-buffer position-in-window)
  (goto-char position-in-buffer)
  (set-window-start (selected-window) position-in-window)
  )

(defun gersemi--on-success (original-buffer start end input-buffer output-buffer error-buffer position-in-buffer position-in-window)
  (gersemi--replace original-buffer start end output-buffer)
  (gersemi--restore-position position-in-buffer position-in-window)
  (mapc 'kill-buffer (list input-buffer output-buffer error-buffer))
  )

(defun gersemi--on-failure (error-code input-buffer output-buffer error-buffer)
  (error
   (message "gersemi exited with error code %d, check %s for details" error-code (buffer-name error-buffer))
   )
  (mapc 'kill-buffer (list input-buffer output-buffer))
  )

(defun gersemi-region (start end)
  "Format region between START and END using gersemi."
  (interactive
   (if (use-region-p)
       (list (region-beginning) (region-end))
     (list (point) (point))
     )
   )

  (let (
        (original (current-buffer))
        (position-in-buffer (point))
        (position-in-window (window-start))
        (input-buffer (get-buffer-create "*gersemi-input*"))
        (output-buffer (get-buffer-create "*gersemi-output*"))
        (error-buffer (get-buffer-create "*gersemi-error*"))
        )
    (gersemi--prepare-buffers original start end input-buffer output-buffer error-buffer)
    (let ((error-code (gersemi--invoke input-buffer output-buffer error-buffer)))
      (if (zerop error-code)
          (gersemi--on-success original start end input-buffer output-buffer error-buffer position-in-buffer position-in-window)
        (gersemi--on-failure error-code input-buffer output-buffer error-buffer)
        )
      )
    )
  )

(defun gersemi-buffer ()
  "Format buffer using gersemi."
  (interactive)
  (gersemi-region (point-min) (point-max))
  )

(define-minor-mode gersemi-mode
  "Run gersemi before saving buffer"
  :lighter " gersemi"
  (if gersemi-mode
      (add-hook 'before-save-hook 'gersemi-buffer nil t)
    (remove-hook 'before-save-hook 'gersemi-buffer t)
    )
  )

(provide 'gersemi)
;;; gersemi.el ends here
