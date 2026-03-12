-- 添加创建人员字段到videos表
ALTER TABLE videos ADD COLUMN created_by VARCHAR(100) DEFAULT '管理员' COMMENT '创建人员';

-- 为现有数据设置创建人员（默认为管理员）
UPDATE videos SET created_by = '管理员' WHERE created_by IS NULL OR created_by = '';

-- 查看更新结果
SELECT id, title, created_by FROM videos LIMIT 10;
