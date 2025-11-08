import React from "react";
import { Link } from "react-router-dom";
import { FaChevronRight } from "react-icons/fa";
import "./Breadcrumbs.css";

const Breadcrumbs = ({ items }) => {
  if (!items || items.length === 0) return null;

  return (
    <nav className="breadcrumbs">
      <ol className="breadcrumbs-list">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <li key={index} className="breadcrumb-item">
              {isLast ? (
                <span className="breadcrumb-current">{item.label}</span>
              ) : (
                <Link to={item.path} className="breadcrumb-link">
                  {item.label}
                </Link>
              )}
              {!isLast && <FaChevronRight className="breadcrumb-separator" />}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
