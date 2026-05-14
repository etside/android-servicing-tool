-- Drop all custom tables and types
DROP TABLE IF EXISTS public.api_usage_logs CASCADE;
DROP TABLE IF EXISTS public.chatbot_training_data CASCADE;
DROP TABLE IF EXISTS public.research_updates CASCADE;
DROP TABLE IF EXISTS public.user_course_progress CASCADE;
DROP TABLE IF EXISTS public.user_purchases CASCADE;
DROP TABLE IF EXISTS public.course_modules CASCADE;
DROP TABLE IF EXISTS public.courses CASCADE;
DROP TABLE IF EXISTS public.user_roles CASCADE;
DROP TABLE IF EXISTS public.profiles CASCADE;

-- Drop trigger on auth.users created by handle_new_user
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Drop functions
DROP FUNCTION IF EXISTS public.handle_new_user() CASCADE;
DROP FUNCTION IF EXISTS public.has_role(uuid, app_role) CASCADE;
DROP FUNCTION IF EXISTS public.update_updated_at_column() CASCADE;

-- Drop enum
DROP TYPE IF EXISTS public.app_role CASCADE;