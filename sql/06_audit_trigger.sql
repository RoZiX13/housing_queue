CREATE TRIGGER trg_housing_queue_audit
AFTER INSERT OR UPDATE OR DELETE ON housing_queue
FOR EACH ROW EXECUTE FUNCTION log_audit_changes();