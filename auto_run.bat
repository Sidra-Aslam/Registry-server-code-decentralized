start "Registry Server" python registry_server.py
timeout 2
start "main.py government0, running on port 4998" python main.py --port 4998 --client government --role owner --id government0
timeout 2
start "main.py government0-dso, running on port 4996" python main.py --port 4996 --client dso --role owner --id government0-dso
timeout 2
start "main.py government0-community, running on port 4994" python main.py --port 4994 --client community --role owner --id government0-community
timeout 2
start "main.py government0-building0, running on port 4992" python main.py --port 4992 --client building --role owner --id government0-building0
timeout 2
start "main.py government0-building0-household0, running on port 4990" python main.py --port 4990 --client household --role owner --id government0-building0-household0
timeout 2
start "main.py government0-building0-household0-occupant0, running on port 4988" python main.py --port 4988 --client occupant --role owner --id government0-building0-household0-occupant0
timeout 2
start "main.py government0-building0-household0-occupant1, running on port 4986" python main.py --port 4986 --client occupant --role business_partner --id government0-building0-household0-occupant1
timeout 2
start "main.py government0-building0-household0-occupant2, running on port 4984" python main.py --port 4984 --client occupant --role public_user --id government0-building0-household0-occupant2
timeout 2
start "main.py government0-building0-household1, running on port 4982" python main.py --port 4982 --client household --role owner --id government0-building0-household1
timeout 2
start "main.py government0-building0-household1-occupant0, running on port 4980" python main.py --port 4980 --client occupant --role owner --id government0-building0-household1-occupant0
timeout 2
start "main.py government0-building0-household1-occupant1, running on port 4978" python main.py --port 4978 --client occupant --role business_partner --id government0-building0-household1-occupant1
timeout 2
start "main.py government0-building0-household1-occupant2, running on port 4976" python main.py --port 4976 --client occupant --role public_user --id government0-building0-household1-occupant2
timeout 2
start "main.py government0-building0-household2, running on port 4974" python main.py --port 4974 --client household --role business_partner --id government0-building0-household2
timeout 2
start "main.py government0-building0-household2-occupant0, running on port 4972" python main.py --port 4972 --client occupant --role owner --id government0-building0-household2-occupant0
timeout 2
start "main.py government0-building0-household2-occupant1, running on port 4970" python main.py --port 4970 --client occupant --role business_partner --id government0-building0-household2-occupant1
timeout 2
start "main.py government0-building0-household2-occupant2, running on port 4968" python main.py --port 4968 --client occupant --role public_user --id government0-building0-household2-occupant2
timeout 2
start "main.py government0-building0-household3, running on port 4966" python main.py --port 4966 --client household --role public_user --id government0-building0-household3
timeout 2
start "main.py government0-building0-household3-occupant0, running on port 4964" python main.py --port 4964 --client occupant --role owner --id government0-building0-household3-occupant0
timeout 2
start "main.py government0-building0-household3-occupant1, running on port 4962" python main.py --port 4962 --client occupant --role business_partner --id government0-building0-household3-occupant1
timeout 2
start "main.py government0-building0-household3-occupant2, running on port 4960" python main.py --port 4960 --client occupant --role public_user --id government0-building0-household3-occupant2
timeout 2
start "main.py government0-building0-household4, running on port 4958" python main.py --port 4958 --client household --role business_partner --id government0-building0-household4
timeout 2
start "main.py government0-building0-household4-occupant0, running on port 4956" python main.py --port 4956 --client occupant --role owner --id government0-building0-household4-occupant0
timeout 2
start "main.py government0-building0-household4-occupant1, running on port 4954" python main.py --port 4954 --client occupant --role business_partner --id government0-building0-household4-occupant1
timeout 2
start "main.py government0-building0-household4-occupant2, running on port 4952" python main.py --port 4952 --client occupant --role public_user --id government0-building0-household4-occupant2
timeout 2
start "main.py government0-building1, running on port 4950" python main.py --port 4950 --client building --role owner --id government0-building1
timeout 2
start "main.py government0-building1-household0, running on port 4948" python main.py --port 4948 --client household --role owner --id government0-building1-household0
timeout 2
start "main.py government0-building1-household0-occupant0, running on port 4946" python main.py --port 4946 --client occupant --role owner --id government0-building1-household0-occupant0
timeout 2
start "main.py government0-building1-household0-occupant1, running on port 4944" python main.py --port 4944 --client occupant --role business_partner --id government0-building1-household0-occupant1
timeout 2
start "main.py government0-building1-household0-occupant2, running on port 4942" python main.py --port 4942 --client occupant --role public_user --id government0-building1-household0-occupant2
timeout 2
start "main.py government0-building1-household1, running on port 4940" python main.py --port 4940 --client household --role owner --id government0-building1-household1
timeout 2
start "main.py government0-building1-household1-occupant0, running on port 4938" python main.py --port 4938 --client occupant --role owner --id government0-building1-household1-occupant0
timeout 2
start "main.py government0-building1-household1-occupant1, running on port 4936" python main.py --port 4936 --client occupant --role business_partner --id government0-building1-household1-occupant1
timeout 2
start "main.py government0-building1-household1-occupant2, running on port 4934" python main.py --port 4934 --client occupant --role public_user --id government0-building1-household1-occupant2
timeout 2
start "main.py government0-building1-household2, running on port 4932" python main.py --port 4932 --client household --role business_partner --id government0-building1-household2
timeout 2
start "main.py government0-building1-household2-occupant0, running on port 4930" python main.py --port 4930 --client occupant --role owner --id government0-building1-household2-occupant0
timeout 2
start "main.py government0-building1-household2-occupant1, running on port 4928" python main.py --port 4928 --client occupant --role business_partner --id government0-building1-household2-occupant1
timeout 2
start "main.py government0-building1-household2-occupant2, running on port 4926" python main.py --port 4926 --client occupant --role public_user --id government0-building1-household2-occupant2
timeout 2
start "main.py government0-building1-household3, running on port 4924" python main.py --port 4924 --client household --role public_user --id government0-building1-household3
timeout 2
start "main.py government0-building1-household3-occupant0, running on port 4922" python main.py --port 4922 --client occupant --role owner --id government0-building1-household3-occupant0
timeout 2
start "main.py government0-building1-household3-occupant1, running on port 4920" python main.py --port 4920 --client occupant --role business_partner --id government0-building1-household3-occupant1
timeout 2
start "main.py government0-building1-household3-occupant2, running on port 4918" python main.py --port 4918 --client occupant --role public_user --id government0-building1-household3-occupant2
timeout 2
start "main.py government0-building1-household4, running on port 4916" python main.py --port 4916 --client household --role business_partner --id government0-building1-household4
timeout 2
start "main.py government0-building1-household4-occupant0, running on port 4914" python main.py --port 4914 --client occupant --role owner --id government0-building1-household4-occupant0
timeout 2
start "main.py government0-building1-household4-occupant1, running on port 4912" python main.py --port 4912 --client occupant --role business_partner --id government0-building1-household4-occupant1
timeout 2
start "main.py government0-building1-household4-occupant2, running on port 4910" python main.py --port 4910 --client occupant --role public_user --id government0-building1-household4-occupant2
timeout 2
start "main.py government0-building2, running on port 4908" python main.py --port 4908 --client building --role business_partner --id government0-building2
timeout 2
start "main.py government0-building2-household0, running on port 4906" python main.py --port 4906 --client household --role owner --id government0-building2-household0
timeout 2
start "main.py government0-building2-household0-occupant0, running on port 4904" python main.py --port 4904 --client occupant --role owner --id government0-building2-household0-occupant0
timeout 2
start "main.py government0-building2-household1, running on port 4902" python main.py --port 4902 --client household --role owner --id government0-building2-household1
timeout 2
start "main.py government0-building2-household1-occupant0, running on port 4900" python main.py --port 4900 --client occupant --role owner --id government0-building2-household1-occupant0
timeout 2
start "main.py government0-building2-household2, running on port 4898" python main.py --port 4898 --client household --role business_partner --id government0-building2-household2
timeout 2
start "main.py government0-building2-household2-occupant0, running on port 4896" python main.py --port 4896 --client occupant --role owner --id government0-building2-household2-occupant0
timeout 2
start "main.py government0-building2-household3, running on port 4894" python main.py --port 4894 --client household --role public_user --id government0-building2-household3
timeout 2
start "main.py government0-building2-household3-occupant0, running on port 4892" python main.py --port 4892 --client occupant --role owner --id government0-building2-household3-occupant0
timeout 2
start "main.py government0-building2-household3-occupant1, running on port 4890" python main.py --port 4890 --client occupant --role business_partner --id government0-building2-household3-occupant1
timeout 2
start "main.py government0-building2-household3-occupant2, running on port 4888" python main.py --port 4888 --client occupant --role public_user --id government0-building2-household3-occupant2
timeout 2
start "main.py government0-building2-household4, running on port 4886" python main.py --port 4886 --client household --role business_partner --id government0-building2-household4
timeout 2
start "main.py government0-building2-household4-occupant0, running on port 4884" python main.py --port 4884 --client occupant --role owner --id government0-building2-household4-occupant0
timeout 2
