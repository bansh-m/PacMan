
(loop :for i from 1 :to 9
    :do(loop :for j from 1 :to 9 
            :do (let ((res (* i j)))
                (if (> 10 res)
                    (format t " ~s" res)
                    (format t " ~s" res))))
        (terpri))
