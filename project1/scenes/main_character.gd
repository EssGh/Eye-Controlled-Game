extends CharacterBody2D

const SPEED = 300.0
const JUMP_VELOCITY = -700.0
const GRAVITY = 1200.0
const GAZE_FILE_PATH = "D:\\MyGodotProjects\\project1\\gaze_direction.txt"
const SCREEN_WIDTH = 1920  # ضع هنا عرض الشاشة أو الحدود المناسبة
const SCREEN_HEIGHT = 1080  # ضع هنا ارتفاع الشاشة أو الحدود المناسبة

@onready var sprite_2d: AnimatedSprite2D = $Sprite2D
@onready var camera: Camera2D = $Camera2D

var gaze_direction: String = "Center"

# تحريك الشخصية إلى اليسار
func move_left():
	velocity.x = -SPEED
	sprite_2d.flip_h = true

# تحريك الشخصية إلى اليمين
func move_right():
	velocity.x = SPEED
	sprite_2d.flip_h = false

# إيقاف حركة الشخصية
func stop_moving():
	velocity.x = 0

# القفز
func jump():
	if is_on_floor():  # تحقق إذا كانت الشخصية على الأرض
		velocity.y = JUMP_VELOCITY

# تحديث الرسوم المتحركة بناءً على الحركة
func update_animation():
	if velocity.x != 0 and is_on_floor():
		sprite_2d.animation = "running"
	elif not is_on_floor():
		if velocity.y < 0:
			sprite_2d.animation = "jumping"
		elif velocity.y > 0:
			sprite_2d.animation = "falling"
	else:
		sprite_2d.animation = "default"

# تحديد حدود الحركة داخل المشهد
func limit_position():
	position.x = clamp(position.x, 0, SCREEN_WIDTH)
	position.y = clamp(position.y, 0, SCREEN_HEIGHT)

# قراءة اتجاه النظرة من الملف النصي
func get_gaze_direction_from_file() -> String:
	var file = FileAccess.open(GAZE_FILE_PATH, FileAccess.READ)
	if file:
		var direction = file.get_as_text().strip_edges()  # قراءة النص وحذف المسافات الزائدة
		file.close()
		return direction
	return "Center"  # إذا لم يكن الملف موجودًا أو لم يحتوي على قيمة

# معالجة الحركة داخل العالم
func _physics_process(delta: float) -> void:
	# تحديث الجاذبية أثناء القفز أو السقوط
	if not is_on_floor():
		velocity.y += GRAVITY * delta

	# قراءة اتجاه النظرة من الملف وتعيين الحركة بناءً عليه
	gaze_direction = get_gaze_direction_from_file()

	# تنفيذ الحركة بناءً على اتجاه النظرة
	match gaze_direction:
		"Left":
			move_left()
		"Right":
			move_right()
		"Center":
			stop_moving()
		"Up":
			jump()  # القفز فقط إذا كانت الشخصية على الأرض
		_:
			pass

	# تحديث الرسوم المتحركة بناءً على الحركة
	update_animation()

	# التأكد من بقاء الشخصية ضمن حدود الشاشة
	limit_position()

	# تطبيق الحركة
	move_and_slide()
