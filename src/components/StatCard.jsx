import { motion } from "framer-motion";

function StatCard({
  title,
  value,
  description,
  icon: Icon,
  className = "",
}) {
  return (
    <motion.div
      className={`stat-card ${className}`}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
    >
      <div className="stat-top">
        <div className="stat-icon">
          <Icon size={19} />
        </div>

        <span className="stat-live">LIVE</span>
      </div>

      <div className="stat-value">
        {value}
      </div>

      <div className="stat-title">
        {title}
      </div>

      <div className="stat-description">
        {description}
      </div>
    </motion.div>
  );
}

export default StatCard;