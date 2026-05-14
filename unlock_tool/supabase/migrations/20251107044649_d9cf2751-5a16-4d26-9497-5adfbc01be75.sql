-- Create table for chatbot training data
CREATE TABLE chatbot_training_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  question_english TEXT NOT NULL,
  question_bengali TEXT NOT NULL,
  answer_english TEXT NOT NULL,
  answer_bengali TEXT NOT NULL,
  module_id UUID REFERENCES course_modules(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Create table for research updates
CREATE TABLE research_updates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  topic TEXT NOT NULL,
  content_english TEXT NOT NULL,
  content_bengali TEXT NOT NULL,
  source_url TEXT,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  created_at TIMESTAMPTZ DEFAULT now(),
  reviewed_by UUID,
  reviewed_at TIMESTAMPTZ
);

-- Create table for API usage tracking
CREATE TABLE api_usage_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,
  api_type TEXT NOT NULL CHECK (api_type IN ('gemini', 'drive')),
  operation TEXT NOT NULL,
  tokens_used INTEGER,
  cost_usd DECIMAL(10, 6),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE chatbot_training_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_updates ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for chatbot_training_data
CREATE POLICY "Admins can manage chatbot training data"
  ON chatbot_training_data FOR ALL
  USING (has_role(auth.uid(), 'admin'));

CREATE POLICY "Students can view training data for purchased courses"
  ON chatbot_training_data FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM user_purchases
      WHERE user_purchases.user_id = auth.uid()
        AND user_purchases.course_id = chatbot_training_data.course_id
        AND user_purchases.payment_status = 'completed'
    ) OR has_role(auth.uid(), 'admin')
  );

-- RLS Policies for research_updates
CREATE POLICY "Admins can manage research updates"
  ON research_updates FOR ALL
  USING (has_role(auth.uid(), 'admin'));

CREATE POLICY "Students can view approved updates"
  ON research_updates FOR SELECT
  USING (status = 'approved' OR has_role(auth.uid(), 'admin'));

-- RLS Policies for api_usage_logs
CREATE POLICY "Admins can view all API logs"
  ON api_usage_logs FOR SELECT
  USING (has_role(auth.uid(), 'admin'));

CREATE POLICY "Users can view own API logs"
  ON api_usage_logs FOR SELECT
  USING (user_id = auth.uid());

-- Triggers for updated_at
CREATE TRIGGER update_chatbot_training_data_updated_at
  BEFORE UPDATE ON chatbot_training_data
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();