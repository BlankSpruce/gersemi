;;; gersemi-tests.el --- test for gersemi.el
(require 'gersemi)
(require 'ert)

;;; Code:
(defun gersemi-tests--make-gersemi-stub ()
  (with-temp-file "gersemi-stub"
    (insert
     "#!/bin/bash
# keep stub alive until EOF appears
cat > /dev/null

if [[ $# -eq 2 ]]; # args are: -- -
then
    echo -n \"Reformatted\"
else
    echo -n \"Reformatted with args:\" $@
fi
")
    )
  (chmod "gersemi-stub" #o755)
  )

(defun gersemi-tests--remove-gersemi-stub ()
  (delete-file "gersemi-stub")
  )

(defun gersemi-tests--with-gersemi-stub (body &optional args)
  (unwind-protect
      (progn
        (gersemi-tests--make-gersemi-stub)
        (setq gersemi-executable (expand-file-name "gersemi-stub"))
        (when args
          (setq gersemi-args args)
          )
        (funcall body)
        )
    (gersemi-tests--remove-gersemi-stub)
    (setq gersemi-executable (eval (car (get 'gersemi-executable 'standard-value))))
    (setq gersemi-args (eval (car (get 'gersemi-args 'standard-value))))
    )
  )

(ert-deftest gersemi-tests--shall-reformat-buffer ()
  "Tests that buffer is reformatted"
  (gersemi-tests--with-gersemi-stub
   (lambda ()
     (with-temp-buffer
       (insert "stuff")
       (gersemi-buffer)
       (should (string-equal "Reformatted" (buffer-string)))
       )
     )
   )
  )

(ert-deftest gersemi-tests--shall-reformat-buffer-with-non-default-args ()
  "Tests that buffer is reformatted when non-default args are set"
  (gersemi-tests--with-gersemi-stub
   (lambda ()
     (with-temp-buffer
       (insert "stuff")
       (gersemi-buffer)
       (should (string-equal "Reformatted with args: -l 120 -- -" (buffer-string)))
       )
     )
   '("-l" "120")
   )
  )

(ert-deftest gersemi-tests--shall-reformat-region ()
  "Tests that region is reformatted"
  (gersemi-tests--with-gersemi-stub
   (lambda ()
     (with-temp-buffer
       (insert "123   789")
       (gersemi-region 4 7)
       (should (string-equal "123Reformatted789" (buffer-string)))
       )
     )
   )
  )

(ert-deftest gersemi-tests--shall-reformat-region-with-non-default-args ()
  "Tests that region is reformatted when non-default args are set"
  (gersemi-tests--with-gersemi-stub
   (lambda ()
     (with-temp-buffer
       (insert "123   789")
       (gersemi-region 4 7)
       (should (string-equal "123Reformatted with args: -l 120 -- -789" (buffer-string)))
       )
     )
   '("-l" "120")
   )
  )

(ert-deftest gersemi-tests--when-gersemi-mode-enabled-shall-reformat-buffer-on-save ()
  "Tests that buffer is reformatted on save when gersemi-mode is enabled"
  (gersemi-tests--with-gersemi-stub
   (lambda ()
     (let ((temp-file-name "gersemi-tests--shall-reformat-buffer-on-save-test-file"))
       (unwind-protect
           (progn
             (find-file temp-file-name)
             (gersemi-mode)
             (insert "stuff")
             (should (string-equal "stuff" (buffer-string)))
             (save-buffer)
             (should (string-equal "Reformatted" (buffer-string)))
             )
         (delete-file temp-file-name)
         )
       )
     )
   )
  )

(ert-deftest gersemi-tests--with-real-gersemi-should-reformat-buffer ()
  "Test that buffer is reformatted with real gersemi"
  (skip-unless (file-executable-p gersemi-executable))
  (with-temp-buffer
    (insert "add_library  (   FOO     BAR    )")
    (gersemi-buffer)
    (should (string-equal (buffer-string) "add_library(FOO BAR)\n"))
    )
  )

(provide 'gersemi-tests)

;;; gersemi-tests.el ends here
