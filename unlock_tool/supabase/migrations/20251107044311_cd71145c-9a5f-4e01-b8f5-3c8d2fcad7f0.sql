-- Courses table
CREATE TABLE courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  title_bengali TEXT NOT NULL,
  description TEXT,
  description_bengali TEXT,
  price DECIMAL(10,2) NOT NULL,
  currency TEXT DEFAULT 'USD' CHECK (currency IN ('USD', 'INR', 'BDT')),
  level TEXT CHECK (level IN ('beginner', 'intermediate', 'advanced')),
  thumbnail_url TEXT,
  preview_video_url TEXT,
  is_published BOOLEAN DEFAULT false,
  total_duration_minutes INTEGER DEFAULT 0,
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Course modules (linked to Google Drive)
CREATE TABLE course_modules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  title_bengali TEXT NOT NULL,
  description TEXT,
  order_index INTEGER NOT NULL,
  drive_file_id TEXT,
  drive_file_name TEXT,
  content_type TEXT CHECK (content_type IN ('video', 'pdf', 'audio', 'text', 'quiz')),
  duration_minutes INTEGER DEFAULT 0,
  is_free_preview BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User purchases
CREATE TABLE user_purchases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  course_id UUID REFERENCES courses(id),
  purchase_date TIMESTAMPTZ DEFAULT NOW(),
  amount_paid DECIMAL(10,2) NOT NULL,
  currency TEXT DEFAULT 'USD',
  payment_method TEXT,
  payment_status TEXT DEFAULT 'completed' CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded')),
  transaction_id TEXT,
  expires_at TIMESTAMPTZ,
  UNIQUE(user_id, course_id)
);

-- Course progress tracking
CREATE TABLE user_course_progress (
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  course_id UUID REFERENCES courses(id),
  module_id UUID REFERENCES course_modules(id),
  completed BOOLEAN DEFAULT false,
  completion_date TIMESTAMPTZ,
  last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
  video_progress_seconds INTEGER DEFAULT 0,
  PRIMARY KEY (user_id, module_id)
);

-- RLS Policies for courses
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view published courses"
  ON courses FOR SELECT
  USING (is_published = true OR created_by = auth.uid());

CREATE POLICY "Admins can manage all courses"
  ON courses FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS for modules (critical for content protection)
ALTER TABLE course_modules ENABLE ROW LEVEL SECURITY;

CREATE POLICY "View modules if purchased or free preview"
  ON course_modules FOR SELECT
  USING (
    is_free_preview = true 
    OR EXISTS (
      SELECT 1 FROM user_purchases 
      WHERE user_id = auth.uid() 
      AND course_id = course_modules.course_id
      AND payment_status = 'completed'
    )
    OR has_role(auth.uid(), 'admin')
  );

CREATE POLICY "Admins can manage modules"
  ON course_modules FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS for purchases
ALTER TABLE user_purchases ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users view own purchases"
  ON user_purchases FOR SELECT
  USING (user_id = auth.uid() OR has_role(auth.uid(), 'admin'));

CREATE POLICY "Admins can manage purchases"
  ON user_purchases FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS for progress
ALTER TABLE user_course_progress ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own progress"
  ON user_course_progress FOR ALL
  USING (user_id = auth.uid());

-- Update trigger for courses
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_courses_updated_at
  BEFORE UPDATE ON courses
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();