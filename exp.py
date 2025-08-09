import asyncio
import logging
import json
from rich.logging import RichHandler
from rich.json import JSON
from rich.markdown import Markdown

from llm_patch_driver.logging import log_wrapper, ArgSpec, OutputFormat
from llm_patch_driver import config

collector = config.build_log_collector(__name__)

logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler(rich_tracebacks=True, markup=True,)])
logging.getLogger("openai").setLevel(logging.WARNING)


TEST_JSON = {
  "name": "Bay Area Oil Drilling, Inc.",
  "address": None,
  "CEO": {
    "first_name": "Mike",
    "last_name": "Popondopulos",
    "personal_contact": None,
    "work_contact": {
      "email": "mike.popondopulos@baod.com",
      "phone": "415-555-1001"
    },
    "address": {
      "street": "500 Howard St, Suite 1200",
      "city": "San Francisco",
      "state": "CA",
      "zip": "94105"
    },
    "department": {
      "department_name": "Executive",
      "employee_title": "Chief Executive Officer",
      "manager_name": None
    },
    "compensation": {
      "base_salary": 410000,
      "bonus": 60000,
      "stock_options": 1900000,
      "total": 2370000
    },
    "distance_from_CEO": 0,
    "subordinates": [
      {
        "first_name": "Rachel",
        "last_name": "Mooney",
        "personal_contact": None,
        "work_contact": {
          "email": "rachel.mooney@baod.com",
          "phone": "415-555-1022"
        },
        "address": {
          "street": "720 Mission St, Apt 21D",
          "city": "San Francisco",
          "state": "CA",
          "zip": "94103"
        },
        "department": {
          "department_name": "Executive",
          "employee_title": "Executive Assistant",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 104000,
          "bonus": 4000,
          "stock_options": 5000,
          "total": 113000
        },
        "distance_from_CEO": 1,
        "subordinates": []
      },
      {
        "first_name": "Carla",
        "last_name": "Gonzalez",
        "personal_contact": None,
        "work_contact": {
          "email": "carla.gonzalez@baod.com",
          "phone": "510-555-2301"
        },
        "address": {
          "street": "880 7th Ave",
          "city": "Oakland",
          "state": "CA",
          "zip": "94606"
        },
        "department": {
          "department_name": "Finance",
          "employee_title": "VP of Finance",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 245000,
          "bonus": 30000,
          "stock_options": 650000,
          "total": 925000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Greg",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Finance",
              "employee_title": "Controller",
              "manager_name": "Carla Gonzalez"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Emily",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Finance",
              "employee_title": "Controller",
              "manager_name": "Carla Gonzalez"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": [
              {
                "first_name": "Tessa",
                "last_name": None,
                "personal_contact": None,
                "work_contact": None,
                "address": None,
                "department": {
                  "department_name": "Finance",
                  "employee_title": "Assistant",
                  "manager_name": "Emily"
                },
                "compensation": None,
                "distance_from_CEO": 3,
                "subordinates": []
              }
            ]
          },
          {
            "first_name": "Jorge",
            "last_name": "Reyes",
            "personal_contact": None,
            "work_contact": {
              "email": "jorge.reyes@baod.com",
              "phone": "510-555-1337"
            },
            "address": {
              "street": "901 Webster St",
              "city": "Oakland",
              "state": "CA",
              "zip": "94607"
            },
            "department": {
              "department_name": "Finance",
              "employee_title": "AP/AR",
              "manager_name": "Carla Gonzalez"
            },
            "compensation": {
              "base_salary": 92000,
              "bonus": 3500,
              "stock_options": 15000,
              "total": 110500
            },
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Aidan",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Finance",
              "employee_title": "Payroll Intern",
              "manager_name": "Carla Gonzalez"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Victor",
        "last_name": "Saldana",
        "personal_contact": None,
        "work_contact": {
          "email": "victor.saldana@baod.com",
          "phone": "650-555-1412"
        },
        "address": {
          "street": "221 Embarcadero Rd",
          "city": "Palo Alto",
          "state": "CA",
          "zip": "94301"
        },
        "department": {
          "department_name": "Legal/Compliance",
          "employee_title": "VP of Legal",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 233000,
          "bonus": 24000,
          "stock_options": 500000,
          "total": 757000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Erica",
            "last_name": "Zhang",
            "personal_contact": None,
            "work_contact": {
              "email": "erica.zhang@baod.com",
              "phone": "408-555-2944"
            },
            "address": {
              "street": "509 Lincoln Ave",
              "city": "San Jose",
              "state": "CA",
              "zip": "95126"
            },
            "department": {
              "department_name": "Legal",
              "employee_title": "Paralegal",
              "manager_name": "Victor Saldana"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Sung",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Legal",
              "employee_title": "Paralegal",
              "manager_name": "Victor Saldana"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Dev",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Legal",
              "employee_title": "Paralegal",
              "manager_name": "Victor Saldana"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Julia",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Legal",
              "employee_title": "Compliance Officer",
              "manager_name": "Victor Saldana"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Brian",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Legal",
              "employee_title": "Risk Manager",
              "manager_name": "Victor Saldana"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Eric",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Legal",
              "employee_title": "Compliance Temp",
              "manager_name": "Victor Saldana"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Lila",
        "last_name": "Chang",
        "personal_contact": None,
        "work_contact": {
          "email": "lila.chang@baod.com",
          "phone": "650-555-8855"
        },
        "address": {
          "street": "394 Castro St",
          "city": "Mountain View",
          "state": "CA",
          "zip": "94041"
        },
        "department": {
          "department_name": "HR",
          "employee_title": "VP of HR",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": None,
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Paul",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "HR",
              "employee_title": "Recruiter",
              "manager_name": "Lila Chang"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Sam",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "HR",
              "employee_title": "Recruiter",
              "manager_name": "Lila Chang"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Linda",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "HR",
              "employee_title": "Benefits",
              "manager_name": "Lila Chang"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Marcus",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "HR",
              "employee_title": "Benefits",
              "manager_name": "Lila Chang"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Michelle",
            "last_name": "Evans",
            "personal_contact": None,
            "work_contact": {
              "email": "michelle.evans@baod.com",
              "phone": "510-555-9911"
            },
            "address": {
              "street": "1234 Franklin St, Apt 4B",
              "city": "Oakland",
              "state": "CA",
              "zip": "94612"
            },
            "department": {
              "department_name": "HR",
              "employee_title": "DEI Officer",
              "manager_name": "Lila Chang"
            },
            "compensation": {
              "base_salary": 129000,
              "bonus": 8000,
              "stock_options": 85000,
              "total": 222000
            },
            "distance_from_CEO": 2,
            "subordinates": [
              {
                "first_name": "Aisha",
                "last_name": None,
                "personal_contact": None,
                "work_contact": None,
                "address": None,
                "department": {
                  "department_name": "HR",
                  "employee_title": "DEI Team",
                  "manager_name": "Michelle Evans"
                },
                "compensation": None,
                "distance_from_CEO": 3,
                "subordinates": []
              },
              {
                "first_name": "Carlos",
                "last_name": None,
                "personal_contact": None,
                "work_contact": None,
                "address": None,
                "department": {
                  "department_name": "HR",
                  "employee_title": "DEI Team",
                  "manager_name": "Michelle Evans"
                },
                "compensation": None,
                "distance_from_CEO": 3,
                "subordinates": []
              }
            ]
          }
        ]
      },
      {
        "first_name": "Peter",
        "last_name": "Thorne",
        "personal_contact": None,
        "work_contact": {
          "email": "peter.thorne@baod.com",
          "phone": "650-555-6623"
        },
        "address": {
          "street": "102 Main St",
          "city": "Redwood City",
          "state": "CA",
          "zip": "94063"
        },
        "department": {
          "department_name": "IT",
          "employee_title": "CTO",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 285000,
          "bonus": 50000,
          "stock_options": 880000,
          "total": 1215000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Kevin",
            "last_name": "Patel",
            "personal_contact": None,
            "work_contact": {
              "email": "kevin.patel@baod.com",
              "phone": "408-555-8880"
            },
            "address": {
              "street": "1725 Willow St",
              "city": "San Jose",
              "state": "CA",
              "zip": "95125"
            },
            "department": {
              "department_name": "IT",
              "employee_title": "DevOps Engineer",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Shilpa",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "DevOps Engineer",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Marcus",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Security Lead",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Ali",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Engineer",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Zach",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Engineer",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Priya",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Engineer",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Lucas",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Engineer",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Jess",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Helpdesk",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Tom",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Helpdesk",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Trevor",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "IT",
              "employee_title": "Helpdesk",
              "manager_name": "Peter Thorne"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Laura",
        "last_name": "Rivas",
        "personal_contact": None,
        "work_contact": {
          "email": "laura.rivas@baod.com",
          "phone": "510-555-3547"
        },
        "address": {
          "street": "19 Beach Dr",
          "city": "Richmond",
          "state": "CA",
          "zip": "94801"
        },
        "department": {
          "department_name": "Operations",
          "employee_title": "VP of Operations",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 195000,
          "bonus": 22500,
          "stock_options": 400000,
          "total": 617500
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Kendrick",
            "last_name": "Steele",
            "personal_contact": None,
            "work_contact": {
              "email": "kendrick.steele@baod.com",
              "phone": "510-555-3255"
            },
            "address": {
              "street": "1919 Grand Ave",
              "city": "Alameda",
              "state": "CA",
              "zip": "94501"
            },
            "department": {
              "department_name": "Operations",
              "employee_title": "Deputy, Field Ops",
              "manager_name": "Laura Rivas"
            },
            "compensation": {
              "base_salary": 147000,
              "bonus": 17000,
              "stock_options": 120000,
              "total": 284000
            },
            "distance_from_CEO": 2,
            "subordinates": [
              {
                "first_name": "Travis",
                "last_name": "Gonzales",
                "personal_contact": None,
                "work_contact": {
                  "email": "travis.gonzales@baod.com",
                  "phone": "650-555-2122"
                },
                "address": {
                  "street": "800 Industrial Rd",
                  "city": "San Carlos",
                  "state": "CA",
                  "zip": "94070"
                },
                "department": {
                  "department_name": "Operations",
                  "employee_title": "Lead Drilling Engineer",
                  "manager_name": "Kendrick Steele"
                },
                "compensation": {
                  "base_salary": 138000,
                  "bonus": 12000,
                  "stock_options": 108000,
                  "total": 158000
                },
                "distance_from_CEO": 3,
                "subordinates": [
                  {
                    "first_name": "Gonzales",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Lin",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Schmidt",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Carter",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Patel",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Nguyen",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Silva",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Lee",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Engineer",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  },
                  {
                    "first_name": "Zoe",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Drilling",
                      "employee_title": "Intern",
                      "manager_name": "Travis Gonzales"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": []
                  }
                ]
              },
              {
                "first_name": "Ethan",
                "last_name": None,
                "personal_contact": None,
                "work_contact": None,
                "address": None,
                "department": {
                  "department_name": "Operations",
                  "employee_title": "Field Tech",
                  "manager_name": "Kendrick Steele"
                },
                "compensation": None,
                "distance_from_CEO": 3,
                "subordinates": []
              },
              {
                "first_name": "Martin",
                "last_name": None,
                "personal_contact": None,
                "work_contact": None,
                "address": None,
                "department": {
                  "department_name": "Operations",
                  "employee_title": "Field Tech",
                  "manager_name": "Kendrick Steele"
                },
                "compensation": None,
                "distance_from_CEO": 3,
                "subordinates": []
              }
            ]
          },
          {
            "first_name": "Sandeep",
            "last_name": "Mehra",
            "personal_contact": None,
            "work_contact": {
              "email": "sandeep.mehra@baod.com",
              "phone": "650-555-7349"
            },
            "address": {
              "street": "2995 Middlefield Rd",
              "city": "Palo Alto",
              "state": "CA",
              "zip": "94306"
            },
            "department": {
              "department_name": "Operations",
              "employee_title": "Deputy, Maintenance & Logistics",
              "manager_name": "Laura Rivas"
            },
            "compensation": {
              "base_salary": 143000,
              "bonus": 14500,
              "stock_options": 90000,
              "total": 247500
            },
            "distance_from_CEO": 2,
            "subordinates": [
              {
                "first_name": "Sharon",
                "last_name": None,
                "personal_contact": None,
                "work_contact": None,
                "address": None,
                "department": {
                  "department_name": "Logistics",
                  "employee_title": "Logistics Manager",
                  "manager_name": "Sandeep Mehra"
                },
                "compensation": None,
                "distance_from_CEO": 3,
                "subordinates": [
                  {
                    "first_name": "Big Mike",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Logistics",
                      "employee_title": "Fleet Supervisor",
                      "manager_name": "Sharon"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": [
                      {
                        "first_name": "Shaun",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Temp Driver",
                          "manager_name": "Big Mike"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      }
                    ]
                  },
                  {
                    "first_name": "Destiny",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Logistics",
                      "employee_title": "Warehouse Supervisor",
                      "manager_name": "Sharon"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": [
                      {
                        "first_name": "Lamar",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Warehouse Tech",
                          "manager_name": "Destiny"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      },
                      {
                        "first_name": "Nick",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Warehouse Tech",
                          "manager_name": "Destiny"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      },
                      {
                        "first_name": "Eileen",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Warehouse Tech",
                          "manager_name": "Destiny"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      },
                      {
                        "first_name": "Rosa",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Warehouse Tech",
                          "manager_name": "Destiny"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      }
                    ]
                  },
                  {
                    "first_name": "Chris",
                    "last_name": None,
                    "personal_contact": None,
                    "work_contact": None,
                    "address": None,
                    "department": {
                      "department_name": "Logistics",
                      "employee_title": "Supervisor",
                      "manager_name": "Sharon"
                    },
                    "compensation": None,
                    "distance_from_CEO": 4,
                    "subordinates": [
                      {
                        "first_name": "David",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Contract Assistant",
                          "manager_name": "Chris"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      },
                      {
                        "first_name": "David",
                        "last_name": None,
                        "personal_contact": None,
                        "work_contact": None,
                        "address": None,
                        "department": {
                          "department_name": "Logistics",
                          "employee_title": "Contract Assistant",
                          "manager_name": "Chris"
                        },
                        "compensation": None,
                        "distance_from_CEO": 5,
                        "subordinates": []
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        "first_name": "Jasmine",
        "last_name": "Shah",
        "personal_contact": None,
        "work_contact": {
          "email": "jasmine.shah@baod.com",
          "phone": "415-555-7282"
        },
        "address": {
          "street": "77 Lombard St",
          "city": "San Francisco",
          "state": "CA",
          "zip": "94111"
        },
        "department": {
          "department_name": "Marketing",
          "employee_title": "VP of Marketing",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 172000,
          "bonus": 18000,
          "stock_options": 320000,
          "total": 510000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Will",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Marketing",
              "employee_title": "Designer",
              "manager_name": "Jasmine Shah"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Mandy",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Marketing",
              "employee_title": "Digital Designer",
              "manager_name": "Jasmine Shah"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Sarah",
            "last_name": "Kim",
            "personal_contact": None,
            "work_contact": {
              "email": "sarah.kim@baod.com",
              "phone": "415-555-9801"
            },
            "address": {
              "street": "230 Divisadero St",
              "city": "San Francisco",
              "state": "CA",
              "zip": "94117"
            },
            "department": {
              "department_name": "Marketing",
              "employee_title": "Content Specialist",
              "manager_name": "Jasmine Shah"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Sean",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Marketing",
              "employee_title": "Content Writer",
              "manager_name": "Jasmine Shah"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Shira",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Marketing",
              "employee_title": "Content Associate",
              "manager_name": "Jasmine Shah"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Dr.",
        "last_name": "Nguyen",
        "personal_contact": None,
        "work_contact": {
          "email": "nguyen.geology@baod.com",
          "phone": "650-555-3200"
        },
        "address": {
          "street": "4100 El Camino Real, Apt 505",
          "city": "Palo Alto",
          "state": "CA",
          "zip": "94306"
        },
        "department": {
          "department_name": "Geology",
          "employee_title": "Director of Geology",
          "manager_name": "Laura Rivas"
        },
        "compensation": {
          "base_salary": 207000,
          "bonus": 25000,
          "stock_options": 325000,
          "total": 557000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Rachel",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Geology",
              "employee_title": "Geologist",
              "manager_name": "Dr. Nguyen"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Benny",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Geology",
              "employee_title": "Geologist",
              "manager_name": "Dr. Nguyen"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Fahim",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Geology",
              "employee_title": "Geologist",
              "manager_name": "Dr. Nguyen"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Julia",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Geology",
              "employee_title": "Junior Geotech",
              "manager_name": "Dr. Nguyen"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Andrew",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Geology",
              "employee_title": "Junior Geotech",
              "manager_name": "Dr. Nguyen"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Kayla",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Geology",
              "employee_title": "Field Assistant",
              "manager_name": "Dr. Nguyen"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Amanda",
        "last_name": "Fields",
        "personal_contact": None,
        "work_contact": {
          "email": "amanda.fields@baod.com",
          "phone": "510-555-8765"
        },
        "address": {
          "street": "2450 Telegraph Ave",
          "city": "Berkeley",
          "state": "CA",
          "zip": "94704"
        },
        "department": {
          "department_name": "Field Safety",
          "employee_title": "Head of Field Safety",
          "manager_name": "Laura Rivas"
        },
        "compensation": {
          "base_salary": 118000,
          "bonus": 6000,
          "stock_options": 40000,
          "total": 164000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Mo",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Field Safety",
              "employee_title": "Site Supervisor",
              "manager_name": "Amanda Fields"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Jeff",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Field Safety",
              "employee_title": "Site Supervisor",
              "manager_name": "Amanda Fields"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Irina",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Field Safety",
              "employee_title": "Safety Tech",
              "manager_name": "Amanda Fields"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Boris",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Field Safety",
              "employee_title": "Safety Tech",
              "manager_name": "Amanda Fields"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Olivia",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Field Safety",
              "employee_title": "Safety Tech",
              "manager_name": "Amanda Fields"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Henry",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Field Safety",
              "employee_title": "Safety Tech",
              "manager_name": "Amanda Fields"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Wendy",
        "last_name": "Sun",
        "personal_contact": None,
        "work_contact": {
          "email": "wendy.sun@baod.com",
          "phone": "650-555-4433"
        },
        "address": {
          "street": "980 Oak Grove Ave",
          "city": "Menlo Park",
          "state": "CA",
          "zip": "94025"
        },
        "department": {
          "department_name": "Environmental",
          "employee_title": "Head of Environmental",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": None,
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Luis",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Environmental",
              "employee_title": "Analyst",
              "manager_name": "Wendy Sun"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Carla",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Environmental",
              "employee_title": "Analyst",
              "manager_name": "Wendy Sun"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Mei",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Environmental",
              "employee_title": "Analyst",
              "manager_name": "Wendy Sun"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Tommy",
        "last_name": "Duarte",
        "personal_contact": None,
        "work_contact": {
          "email": "tommy.duarte@baod.com",
          "phone": "415-555-1127"
        },
        "address": {
          "street": "1110 Polk St",
          "city": "San Francisco",
          "state": "CA",
          "zip": "94109"
        },
        "department": {
          "department_name": "Sales",
          "employee_title": "Head of Sales",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": None,
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Sandra",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Account Exec",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Paul",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Account Exec",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Maggie",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Account Exec",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Raj",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Account Exec",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Felipe",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Account Exec",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Ginny",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Sales-Ops Analyst",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Olivia",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Sales-Ops Analyst",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Dan",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Sales",
              "employee_title": "Sales-Ops Analyst",
              "manager_name": "Tommy Duarte"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Gina",
        "last_name": "Obrien",
        "personal_contact": None,
        "work_contact": {
          "email": "gina.obrien@baod.com",
          "phone": "510-555-7000"
        },
        "address": {
          "street": "3300 Laguna Ave",
          "city": "Oakland",
          "state": "CA",
          "zip": "94602"
        },
        "department": {
          "department_name": "Procurement",
          "employee_title": "Head of Procurement",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": {
          "base_salary": 154000,
          "bonus": 10000,
          "stock_options": 60000,
          "total": 224000
        },
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Lisa",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Procurement",
              "employee_title": "Buyer",
              "manager_name": "Gina Obrien"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Gordon",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Procurement",
              "employee_title": "Buyer",
              "manager_name": "Gina Obrien"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "James",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Procurement",
              "employee_title": "Contract Admin",
              "manager_name": "Gina Obrien"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Mary",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Procurement",
              "employee_title": "Contract Admin",
              "manager_name": "Gina Obrien"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Owen",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Procurement",
              "employee_title": "Contract Admin",
              "manager_name": "Gina Obrien"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Jacob",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "Procurement",
              "employee_title": "Inventory Manager",
              "manager_name": "Gina Obrien"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Dr. Roberts",
        "last_name": None,
        "personal_contact": None,
        "work_contact": None,
        "address": None,
        "department": {
          "department_name": "R&D",
          "employee_title": "Head of R&D",
          "manager_name": "Mike Popondopulos"
        },
        "compensation": None,
        "distance_from_CEO": 1,
        "subordinates": [
          {
            "first_name": "Priya",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "R&D",
              "employee_title": "Research Engineer",
              "manager_name": "Dr. Roberts"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Hassan",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "R&D",
              "employee_title": "Research Engineer",
              "manager_name": "Dr. Roberts"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          },
          {
            "first_name": "Nikhil",
            "last_name": None,
            "personal_contact": None,
            "work_contact": None,
            "address": None,
            "department": {
              "department_name": "R&D",
              "employee_title": "Data Scientist",
              "manager_name": "Dr. Roberts"
            },
            "compensation": None,
            "distance_from_CEO": 2,
            "subordinates": []
          }
        ]
      },
      {
        "first_name": "Ed",
        "last_name": None,
        "personal_contact": None,
        "work_contact": None,
        "address": None,
        "department": {
          "department_name": "Facilities",
          "employee_title": "Cafeteria",
          "manager_name": None
        },
        "compensation": None,
        "distance_from_CEO": 1,
        "subordinates": []
      },
      {
        "first_name": "Julia",
        "last_name": None,
        "personal_contact": None,
        "work_contact": None,
        "address": None,
        "department": {
          "department_name": "Facilities",
          "employee_title": "Cafeteria",
          "manager_name": None
        },
        "compensation": None,
        "distance_from_CEO": 1,
        "subordinates": []
      }
    ]
  },
  "avg_compensation": 495704,
  "num_of_departments": 11
}

template = """
```json
{object_content}
```
        """

@log_wrapper(
    #log_input=[ArgSpec(name="x", rich_console=JSON)],
    log_output=OutputFormat(rich_console=Markdown),
    span_kind="tool",
)
async def to_json(x: str) -> str:
    return x

if __name__ == "__main__":
    test_json = json.dumps(TEST_JSON, indent=4)
    asyncio.run(to_json(template.format(object_content=test_json)))