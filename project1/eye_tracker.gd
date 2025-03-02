extends Node2D
var output_file_path:String = "res://output/aaa.txt"
signal gaze_direction_changed(direction: String)

var last_direction: String = ""

func _process(delta):
	var file = FileAccess.open(output_file_path, FileAccess.READ)
	if file != null and file.is_open():
		var direction = file.get_as_text().strip_edges()
		file.close()
		
		if direction != "" and direction != last_direction:
			last_direction = direction
			emit_signal("gaze_direction_changed", direction)
			print("Read direction:", direction)
